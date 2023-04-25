import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSlider, QPushButton,
                             QStyle, QFileDialog, QWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtMultimedia import QAbstractVideoSurface, QVideoFrame, QVideoSurfaceFormat
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSizePolicy

class VideoFrameCapture(QAbstractVideoSurface):
    frame_captured = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = None

    def supportedPixelFormats(self, handleType):
        return [QVideoFrame.Format_RGB32, QVideoFrame.Format_ARGB32, QVideoFrame.Format_ARGB32_Premultiplied]

    def present(self, frame):
        self.current_frame = frame
        self.frame_captured.emit()
        return True

    def get_current_frame(self):
        if self.current_frame:
            return self.current_frame.image()
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.image_count = 0
        self.output_folder = "output"

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        self.capture_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.capture_surface = VideoFrameCapture()
        self.capture_player.setVideoOutput(self.capture_surface)
        self.capture_player.setMuted(True)

        self.init_ui()

    def init_ui(self):
      # Create a QWidget to hold the UI elements
      central_widget = QWidget(self)
      self.setCentralWidget(central_widget)

      # Create a QVBoxLayout to hold the main layout
      main_layout = QVBoxLayout()

      # Create and set up the video playback area
      self.video_widget = QVideoWidget()
      main_layout.addWidget(self.video_widget)
      self.media_player.setVideoOutput(self.video_widget)
      self.media_player.durationChanged.connect(self.update_slider_range)
      self.media_player.positionChanged.connect(self.update_slider_position)

      # Create and set up the playback controls
      controls_layout = QHBoxLayout()
      self.open_button = QPushButton("Open File")
      self.open_button.clicked.connect(self.open_video_file)
      controls_layout.addWidget(self.open_button)

      self.play_button = QPushButton()
      self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
      self.play_button.clicked.connect(self.play_pause)
      controls_layout.addWidget(self.play_button)

      self.slider = QSlider()
      self.slider.setOrientation(Qt.Horizontal)
      self.slider.sliderMoved.connect(self.move_slider)
      controls_layout.addWidget(self.slider)

      self.frame_button = QPushButton("Next Frame")
      self.frame_button.clicked.connect(self.next_frame)
      controls_layout.addWidget(self.frame_button)

      main_layout.addLayout(controls_layout)

      # Create and set up the export frame button
      self.export_button = QPushButton("Export Frame")
      self.export_button.clicked.connect(self.export_frame)
      main_layout.addWidget(self.export_button)

      # Create and set up the current frame label
      self.frame_label = QLabel("Frame: 0")
      main_layout.addWidget(self.frame_label)

      frame_label_size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
      self.frame_label.setSizePolicy(frame_label_size_policy)

      # Set up the main layout and window properties
      central_widget.setLayout(main_layout)
      self.setWindowTitle("Video Frame Exporter")

    def update_slider_range(self, duration):
        self.slider.setMinimum(0)
        self.slider.setMaximum(duration)

    def open_video_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.flv *.mov *.wmv);;All Files (*)", options=options)
        if file_name:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.play_button.setEnabled(True)

    def play_pause(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def update_slider_position(self, position):
        # Prevent triggering the move_slider method while updating the slider value
        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)

    def move_slider(self, position):
        if self.media_player.isSeekable():
            self.media_player.setPosition(position)

    def next_frame(self):
        # Calculate the duration of one frame in milliseconds
        fps = 30  # Assuming 30 frames per second, you may need to adjust this based on the video's actual frame rate
        frame_duration = 1000 / fps

        # Pause the video if it's playing
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        # Move the video position one frame forward
        current_position = self.media_player.position()
        new_position = current_position + frame_duration
        self.media_player.setPosition(new_position)

        # Update the displayed frame number
        current_frame = int(new_position / frame_duration)
        self.frame_label.setText(f"Frame: {current_frame}")


    def export_frame(self):
        # Prepare the capture player and surface
        capture_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        capture_surface = VideoFrameCapture()
        capture_player.setVideoOutput(capture_surface)
        capture_player.setMuted(True)

        # Set the media and position of the capture player
        capture_player.setMedia(self.media_player.currentMedia())
        capture_player.setPosition(self.media_player.position())
        capture_player.pause()

        # Wait for a frame to be captured
        loop = QEventLoop()
        capture_surface.frame_captured.connect(loop.quit)
        loop.exec_()

        # Capture the current frame
        current_frame = capture_surface.get_current_frame()
        if current_frame:
            print(f"Image properties: size={current_frame.size()}, format={current_frame.format()}")

            # Save the frame as an image file
            image_file_name = f"frame_{self.image_count:04d}.png"
            image_file_path = os.path.join(self.output_folder, image_file_name)
            success = current_frame.save(image_file_path, "PNG")

            if success:
                print("File saving: Succeeded")
                # Increment the image count
                self.image_count += 1
            else:
                print("File saving: Failed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
