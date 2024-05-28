from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt
from PIL import Image, ImageSequence
import os
import sys
import shutil

def split_gif(input_gif, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    frame_durations = []

    with Image.open(input_gif) as im:
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            frame = frame.convert("RGBA")
            frame.save(f"{output_folder}/frame_{i:03d}.png")
            frame_durations.append(frame.info['duration'])

    print(f"GIF split into frames and saved in {output_folder}")
    return frame_durations

def reassemble_gif(input_folder, output_gif, frame_durations):
    frames = []
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.png'):
            frame_path = os.path.join(input_folder, filename)
            frames.append(Image.open(frame_path).convert("RGBA"))

    if not frames:
        raise ValueError("No valid frames found in the input folder.")

    if not output_gif.lower().endswith('.gif'):
        output_gif += '.gif'

    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=frame_durations,
        loop=0,
        disposal=2
    )
    print(f"Frames reassembled into GIF and saved as {output_gif}")

def upscale_sprite(input_path, output_path, scale_factor):
    img = Image.open(input_path).convert("RGBA")
    new_size = (img.width * scale_factor, img.height * scale_factor)
    upscaled_img = img.resize(new_size, Image.NEAREST)
    upscaled_img.save(output_path)

def upscale_frames(input_folder, output_folder, scale_factor):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            upscale_sprite(input_path, output_path, scale_factor)

def process_images(input_directory, output_directory, scale_factor):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(('.gif', '.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_directory, filename)
            file_format = filename.split('.')[-1].lower()
            format_output_directory = os.path.join(output_directory, file_format)

            if not os.path.exists(format_output_directory):
                os.makedirs(format_output_directory)

            if filename.endswith('.gif'):
                temp_folder = "temp_frames"
                upscaled_folder = "upscaled_frames"

                frame_durations = split_gif(input_path, temp_folder)
                upscale_frames(temp_folder, upscaled_folder, scale_factor)
                output_gif = os.path.join(format_output_directory, filename)
                reassemble_gif(upscaled_folder, output_gif, frame_durations)

                shutil.rmtree(temp_folder)
                shutil.rmtree(upscaled_folder)
            else:
                output_path = os.path.join(format_output_directory, filename)
                upscale_sprite(input_path, output_path, scale_factor)

class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        self.input_dir_label = QLabel("No input directory selected")
        self.input_dir_button = QPushButton("Select input directory")
        self.input_dir_button.clicked.connect(self.select_input_directory)

        self.scale_factor_label = QLabel("Select scale factor:")
        self.scale_factor_spinbox = QSpinBox()
        self.scale_factor_spinbox.setRange(1, 10)
        self.scale_factor_spinbox.setValue(2)

        self.process_button = QPushButton("Start processing")
        self.process_button.clicked.connect(self.start_processing)

        layout.addWidget(self.input_dir_label)
        layout.addWidget(self.input_dir_button)
        layout.addWidget(self.scale_factor_label)
        layout.addWidget(self.scale_factor_spinbox)
        layout.addWidget(self.process_button)

        self.setLayout(layout)
        self.setWindowTitle("Sprite Upscaler")
        self.setGeometry(300, 300, 300, 200)

    def select_input_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select input Directory")
        if directory:
            self.input_dir_label.setText(directory)
            self.input_directory = directory

    def start_processing(self):
        try:
            input_directory = self.input_directory
            output_directory = "output"
            scale_factor = self.scale_factor_spinbox.value()

            process_images(input_directory, output_directory, scale_factor)
            QMessageBox.information(self, "Process Complete", "All images have been processed and saved to the output directory.")
        except AttributeError:
            QMessageBox.warning(self, "Input Directory Not Selected", "Please select an input directory before starting the processing.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ImageProcessorApp()
    ex.show()
    sys.exit(app.exec())
