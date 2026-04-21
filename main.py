import sys
import os
import time
import traceback
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

ROWDY_FONT_FAMILY = "Arial"

class CircularProfile(QWidget):
    name_changed = pyqtSignal(str, str)
    profile_clicked = pyqtSignal(str)
    
    def __init__(self, profile_id, name="Speaker", parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.display_name = name
        self.is_speaking = False
        self.base_glow_color = QColor(0, 192, 255)
        self.profile_pixmap = None
        self._glow_intensity = 0.0

        self.glow_anim = QVariantAnimation(self)
        self.glow_anim.setDuration(800)
        self.glow_anim.setStartValue(0.0)
        self.glow_anim.setEndValue(1.0)
        self.glow_anim.setEasingCurve(QEasingCurve.SineCurve)
        self.glow_anim.setLoopCount(-1)
        self.glow_anim.valueChanged.connect(self._update_glow)

        self.editor = QLineEdit(self)
        self.editor.setVisible(False)
        self.editor.setAlignment(Qt.AlignCenter)
        self.editor.editingFinished.connect(self._finish_rename)
        self.editor.setStyleSheet("background: #111; color: white; border: 1px solid #00d2ff;")

    def _update_glow(self, value):
        self._glow_intensity = value
        self.update()

    def set_speaking(self, speaking):
        if self.is_speaking != speaking:
            self.is_speaking = speaking
            if speaking: self.glow_anim.start()
            else: 
                self.glow_anim.stop()
                self._glow_intensity = 0
            self.update()

    def set_profile_image(self, path):
        pix = QPixmap(path)
        if not pix.isNull():
            self.profile_pixmap = pix
            self.update()

    def mouseDoubleClickEvent(self, event):
        self.editor.setText(self.display_name)
        ew, eh = int(self.width()*0.7), 22
        self.editor.setGeometry((self.width()-ew)//2, self.height() - eh - 35, ew, eh)
        self.editor.setVisible(True)
        self.editor.setFocus()

    def _finish_rename(self):
        new_name = self.editor.text()
        if new_name:
            self.display_name = new_name
            self.name_changed.emit(self.profile_id, new_name)
        self.editor.setVisible(False)
        self.update()

    def mousePressEvent(self, event):
        self.profile_clicked.emit(self.profile_id)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(35, 35, -35, -35)
        
        if self.is_speaking:
            glow_color = QColor(self.base_glow_color)
            glow_color.setAlpha(int(40 + 160 * self._glow_intensity))
            p.setPen(QPen(glow_color, 12.0 + 30.0 * self._glow_intensity))
            p.drawEllipse(rect)

        p.save()
        path = QPainterPath()
        path.addEllipse(rect)
        p.setClipPath(path)
        if self.profile_pixmap:
            p.drawPixmap(rect.toRect(), self.profile_pixmap.scaled(
                rect.size().toSize(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            p.setBrush(QColor(25, 25, 35))
            p.setPen(Qt.NoPen); p.drawEllipse(rect)
        p.restore()

        border_pen = QPen(QColor(255, 255, 255, 60))
        border_pen.setWidth(2)
        p.setPen(border_pen); p.drawEllipse(rect)

        if not self.editor.isVisible():
            p.setPen(Qt.white)
            font_size = max(6, int(rect.width() * 0.055))
            p.setFont(QFont(ROWDY_FONT_FAMILY, font_size, QFont.Medium))
            text_rect = rect.adjusted(5, 0, -5, -12)
            p.drawText(text_rect, Qt.AlignBottom | Qt.AlignHCenter, self.display_name)

class AudioPlaybackThread(QThread):
    speaker_active = pyqtSignal(str, bool)
    finished = pyqtSignal()

    def __init__(self, initial_profiles, volumes):
        super().__init__()
        self._running = True
        self.samplerate = 44100
        self.active_tracks = {}
        self.track_volumes = volumes
        self._lock = QMutex()
        self.master_cursor = 0
        self.gain_divisor = max(1, len(initial_profiles))
        for p in initial_profiles: self.add_track(p['id'], p['path'])

    def update_volume(self, p_id, vol):
        self._lock.lock(); self.track_volumes[p_id] = vol; self._lock.unlock()

    def add_track(self, p_id, path):
        try:
            seg = AudioSegment.from_file(path).set_frame_rate(self.samplerate).set_channels(1)
            samples = np.array(seg.get_array_of_samples()).astype(np.float32) / 32768.0
            self._lock.lock()
            start_pos = self.master_cursor
            if start_pos < len(samples):
                self.active_tracks[p_id] = {'samples': samples, 'cursor': start_pos}
            self._lock.unlock()
        except Exception: traceback.print_exc()

    def run(self):
        try:
            block_size = 2048
            with sd.OutputStream(samplerate=self.samplerate, channels=1, dtype='float32') as stream:
                while self._running:
                    self._lock.lock()
                    if not self.active_tracks:
                        self._lock.unlock(); time.sleep(0.1); continue

                    mixed_block = np.zeros(block_size, dtype=np.float32)
                    has_active = False
                    track_ids = list(self.active_tracks.keys())
                    for tid in track_ids:
                        track = self.active_tracks[tid]
                        vol = self.track_volumes.get(tid, 1.0)
                        start = track['cursor']; end = start + block_size
                        chunk = track['samples'][start:end]
                        if len(chunk) > 0:
                            v_peak = 20 * np.log10(np.max(np.abs(chunk)) + 1e-9)
                            self.speaker_active.emit(tid, bool(v_peak > -25 and vol > 0.01))
                            if len(chunk) < block_size: chunk = np.pad(chunk, (0, block_size - len(chunk)))
                            mixed_block += (chunk * vol)
                            track['cursor'] += block_size
                            has_active = True
                        else:
                            self.speaker_active.emit(tid, False)
                            del self.active_tracks[tid]
                    self._lock.unlock()
                    if has_active:
                        stream.write(mixed_block / self.gain_divisor)
                        self.master_cursor += block_size
                    else: break
        except Exception: traceback.print_exc()
        finally: self.finished.emit()

    def stop(self): self._running = False

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(450, 1000)
        self.setWindowTitle("DallVoice Mixer")
        self.profiles = {} 
        self.is_dark = True
        self.playback_thread = None
        self.setup_ui()
        QTimer.singleShot(200, self.add_profile)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0)
        header = QFrame(); header.setFixedHeight(70); h_layout = QHBoxLayout(header)
        self.menu_btn = QPushButton("☰"); self.menu_btn.setFixedSize(45, 45)
        self.menu_btn.clicked.connect(self.toggle_left_menu)
        self.settings_btn = QPushButton("⚙"); self.settings_btn.setFixedSize(45, 45)
        self.settings_btn.clicked.connect(self.toggle_right_menu)
        h_layout.addWidget(self.menu_btn); h_layout.addStretch(); h_layout.addWidget(self.settings_btn)
        self.main_layout.addWidget(header)
        self.container = QWidget(); self.main_layout.addWidget(self.container, 1)
        self.play_btn = QPushButton("►"); self.play_btn.setFixedSize(85, 85)
        self.play_btn.setObjectName("playBtn"); self.play_btn.clicked.connect(self.toggle_play)
        self.main_layout.addWidget(self.play_btn, 0, Qt.AlignCenter); self.main_layout.addSpacing(50)

        # Left Menu
        self.left_menu = QFrame(self); self.left_menu.setFixedWidth(320); self.left_menu.setObjectName("sideMenu")
        self.left_menu.move(-320, 0)
        lm_layout = QVBoxLayout(self.left_menu)
        lm_c = QHBoxLayout(); lm_c.addStretch(); cb = QPushButton("✕")
        cb.setFixedSize(35,35); cb.clicked.connect(self.toggle_left_menu); lm_c.addWidget(cb); lm_layout.addLayout(lm_c)
        lm_layout.addWidget(QLabel("MANAGEMENT"), alignment=Qt.AlignCenter)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget(); self.card_layout = QVBoxLayout(self.scroll_content)
        self.card_layout.setAlignment(Qt.AlignTop); self.scroll.setWidget(self.scroll_content)
        lm_layout.addWidget(self.scroll)
        self.add_btn = QPushButton("+ Add Profile"); self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_profile); lm_layout.addWidget(self.add_btn)

        # Right Menu
        self.right_menu = QFrame(self); self.right_menu.setFixedWidth(240); self.right_menu.setObjectName("sideMenu")
        self.right_menu.move(self.width(), 0)
        rm_layout = QVBoxLayout(self.right_menu)
        rm_c = QHBoxLayout(); rb = QPushButton("✕"); rb.setFixedSize(35,35)
        rb.clicked.connect(self.toggle_right_menu); rm_c.addWidget(rb); rm_c.addStretch(); rm_layout.addLayout(rm_c)
        rm_layout.addWidget(QLabel("SETTINGS"), alignment=Qt.AlignCenter)
        t_btn = QPushButton("Switch Theme"); t_btn.setMinimumHeight(40); t_btn.clicked.connect(self.toggle_theme)
        rm_layout.addWidget(t_btn); rm_layout.addStretch()

        self.apply_styles()

    def add_profile(self):
        if len(self.profiles) >= 5: return
        p_id = str(time.time())
        name = f"Speaker {len(self.profiles) + 1}"
        w = CircularProfile(p_id, name, self.container)
        w.name_changed.connect(self.sync_name_to_card); w.profile_clicked.connect(self.change_profile_image)
        w.show()
        
        card = QFrame(); card.setMinimumHeight(160); card.setObjectName("card")
        cl = QVBoxLayout(card)
        ni = QLineEdit(name); ni.textChanged.connect(lambda t, i=p_id: self.sync_name_to_widget(i, t))
        
        row1 = QHBoxLayout(); aud = QPushButton("Audio")
        aud.clicked.connect(lambda _, i=p_id: self.link_audio(i))
        
        # Visibility Button
        vis_btn = QPushButton("👁️"); vis_btn.setFixedSize(35, 30)
        vis_btn.clicked.connect(lambda _, i=p_id: self.toggle_visibility(i))
        
        dele = QPushButton("✕"); dele.setFixedSize(30, 30); dele.setObjectName("delBtn")
        dele.clicked.connect(lambda _, i=p_id: self.remove_profile(i))
        row1.addWidget(aud); row1.addWidget(vis_btn); row1.addWidget(dele)
        
        row2 = QHBoxLayout(); mute = QPushButton("🔊"); mute.setFixedSize(35, 30)
        vol_slider = QSlider(Qt.Horizontal); vol_slider.setRange(0, 100); vol_slider.setValue(100)
        row2.addWidget(mute); row2.addWidget(vol_slider)
        vol_slider.valueChanged.connect(lambda v, i=p_id: self.update_volume(i, v/100.0))
        mute.clicked.connect(lambda _, i=p_id: self.toggle_mute(i))

        cl.addWidget(ni); cl.addLayout(row1); cl.addLayout(row2)
        self.card_layout.addWidget(card)
        
        self.profiles[p_id] = {
            'widget': w, 'card': card, 'audio': None, 'aud_btn': aud, 
            'del_btn': dele, 'vis_btn': vis_btn, 'vol': 1.0, 'is_muted': False, 
            'is_visible': True, 'mute_btn': mute, 'slider': vol_slider
        }
        self.rearrange_profiles()

    def toggle_visibility(self, p_id):
        p = self.profiles[p_id]
        p['is_visible'] = not p['is_visible']
        p['vis_btn'].setText("👁️" if p['is_visible'] else "👁️‍🗨️")
        if p['is_visible']: p['widget'].show()
        else: p['widget'].hide()
        self.rearrange_profiles()

    def update_volume(self, p_id, val):
        self.profiles[p_id]['vol'] = val
        if not self.profiles[p_id]['is_muted'] and self.playback_thread:
            self.playback_thread.update_volume(p_id, val)

    def toggle_mute(self, p_id):
        p = self.profiles[p_id]
        p['is_muted'] = not p['is_muted']
        p['mute_btn'].setText("🔇" if p['is_muted'] else "🔊")
        target_vol = 0.0 if p['is_muted'] else p['vol']
        if self.playback_thread: self.playback_thread.update_volume(p_id, target_vol)

    def remove_profile(self, p_id):
        if self.playback_thread and self.playback_thread.isRunning():
            QMessageBox.warning(self, "Action Denied", "Cannot delete profiles during streaming.")
            return
        if len(self.profiles) <= 1: return
        data = self.profiles.pop(p_id)
        data['widget'].deleteLater(); data['card'].deleteLater()
        QTimer.singleShot(100, self.rearrange_profiles)

    def sync_name_to_card(self, p_id, name):
        le = self.profiles[p_id]['card'].findChild(QLineEdit)
        if le: le.blockSignals(True); le.setText(name); le.blockSignals(False)

    def sync_name_to_widget(self, p_id, name):
        self.profiles[p_id]['widget'].display_name = name; self.profiles[p_id]['widget'].update()

    def link_audio(self, p_id):
        path, _ = QFileDialog.getOpenFileName(self, "Select Audio", "", "Audio (*.mp3 *.wav *.ogg)")
        if path:
            self.profiles[p_id]['audio'] = path
            self.profiles[p_id]['aud_btn'].setText("Linked ✓")
            if self.playback_thread and self.playback_thread.isRunning():
                self.playback_thread.add_track(p_id, path)

    def change_profile_image(self, p_id):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.profiles[p_id]['widget'].set_profile_image(path)

    def toggle_play(self):
        if self.playback_thread and self.playback_thread.isRunning():
            self.playback_thread.stop(); return
        valid_files = []; vol_map = {}
        for p_id, d in self.profiles.items():
            if d['audio']: 
                valid_files.append({'id': p_id, 'path': d['audio']})
                vol_map[p_id] = 0.0 if d['is_muted'] else d['vol']
        if not valid_files: return
        self.play_btn.setText("■"); self.play_btn.setStyleSheet("background: #ff4500;")
        self.lock_ui(True)
        self.playback_thread = AudioPlaybackThread(valid_files, vol_map)
        self.playback_thread.speaker_active.connect(lambda i, a: self.profiles[i]['widget'].set_speaking(a) if i in self.profiles else None)
        self.playback_thread.finished.connect(self.on_playback_end); self.playback_thread.start()

    def on_playback_end(self):
        self.play_btn.setText("►"); self.play_btn.setStyleSheet("")
        self.lock_ui(False)
        for d in self.profiles.values(): d['widget'].set_speaking(False)

    def lock_ui(self, locked):
        for d in self.profiles.values(): d['del_btn'].setEnabled(not locked)

    def rearrange_profiles(self):
        # FILTER ONLY VISIBLE PROFILES
        visible_items = [p for p in self.profiles.values() if p['is_visible']]
        count = len(visible_items)
        widgets = [p['widget'] for p in visible_items]
        
        cw, ch = self.container.width(), self.container.height()
        if cw < 50: cw, ch = self.width(), self.height()-200
        
        if count == 0: return # Nothing to draw
        
        if count == 1:
            s = int(min(cw, ch) * 0.65)
            widgets[0].setGeometry(int((cw-s)/2), int((ch-s)/2), s, s)
        elif count == 2:
            s = int(min(cw, ch) * 0.52)
            widgets[0].setGeometry(int((cw-s)/2), int(ch/3.5 - s/2), s, s)
            widgets[1].setGeometry(int((cw-s)/2), int(ch - ch/3.5 - s/2), s, s)
        else:
            scale_map = {3: 0.46, 4: 0.44, 5: 0.40}
            orbit_map = {3: 0.20, 4: 0.23, 5: 0.24}
            s = int(min(cw, ch) * scale_map.get(count, 0.4))
            radius = min(cw, ch) * orbit_map.get(count, 0.25)
            for i, w in enumerate(widgets):
                angle = (2 * np.pi / count) * i - (np.pi/2)
                x = (cw/2) + (radius * np.cos(angle)) - s/2
                y = (ch/2) + (radius * np.sin(angle)) - s/2
                w.setGeometry(int(x), int(y), s, s)

    def toggle_left_menu(self):
        self.anim_l = QPropertyAnimation(self.left_menu, b"pos"); self.anim_l.setDuration(300)
        end_x = 0 if self.left_menu.x() < 0 else -320
        self.anim_l.setEndValue(QPoint(end_x, 0)); self.anim_l.setEasingCurve(QEasingCurve.OutCubic); self.anim_l.start()

    def toggle_right_menu(self):
        self.anim_r = QPropertyAnimation(self.right_menu, b"pos"); self.anim_r.setDuration(300)
        end_x = self.width() - 240 if self.right_menu.x() >= self.width() else self.width()
        self.anim_r.setEndValue(QPoint(end_x, 0)); self.anim_r.setEasingCurve(QEasingCurve.OutCubic); self.anim_r.start()

    def toggle_theme(self): self.is_dark = not self.is_dark; self.apply_styles()

    def apply_styles(self):
        bg = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #090912, stop:1 #151525)" if self.is_dark else "#f0f0f5"
        txt = "white" if self.is_dark else "#1a1a1a"
        sb = "rgba(15, 15, 25, 250)" if self.is_dark else "rgba(255, 255, 255, 250)"
        self.setStyleSheet(f"""
            QWidget {{ background: {bg}; color: {txt}; font-family: '{ROWDY_FONT_FAMILY}'; }}
            #sideMenu {{ background: {sb}; border: 1px solid #333; }}
            #card {{ background: rgba(100,100,100,20); border-radius: 12px; }}
            QPushButton {{ background: #1e1e30; border-radius: 8px; color: white; border: none; font-weight: bold; }}
            QPushButton#playBtn {{ background: #00d2ff; border-radius: 42px; font-size: 30px; color: #090912; }}
            QPushButton#delBtn {{ background: #800; }}
            QPushButton#delBtn:disabled {{ background: #444; color: #888; }}
            QLineEdit {{ background: rgba(0,0,0,40); border: 1px solid #444; border-radius: 6px; padding: 4px; color: {txt}; }}
            QSlider::handle:horizontal {{ background: #00d2ff; border-radius: 5px; width: 14px; }}
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.rearrange_profiles()
        self.left_menu.setFixedHeight(self.height()); self.right_menu.setFixedHeight(self.height())
        if self.right_menu.x() < self.width(): self.right_menu.move(self.width()-240, 0)
        else: self.right_menu.move(self.width(), 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    f_path = "Rowdy-Regular.ttf"
    if os.path.exists(f_path):
        fid = QFontDatabase.addApplicationFont(f_path)
        if fid != -1: ROWDY_FONT_FAMILY = QFontDatabase.applicationFontFamilies(fid)[0]
    win = MainApp(); win.show(); sys.exit(app.exec_())