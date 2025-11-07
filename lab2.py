import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QComboBox, QLabel,
                             QFileDialog, QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget,
                             QSlider)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

# Морфологическая оброботка

class MorphologyTab(QWidget):
    """
    Вкладка для демонстрации морфологической обработки изображений.
    """
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.processed_image = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        left_panel = QVBoxLayout()
        
        load_group = QGroupBox("Загрузка изображения")
        load_layout = QVBoxLayout()
        self.load_btn = QPushButton("Загрузить изображение")
        self.load_btn.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_btn)
        load_group.setLayout(load_layout)
        left_panel.addWidget(load_group)
        
        params_group = QGroupBox("Параметры ядра")
        params_layout = QVBoxLayout()
        
        params_layout.addWidget(QLabel("Структурирующий элемент:"))
        self.struct_element_combo = QComboBox()
        self.struct_element_combo.addItems(["Прямоугольник", "Эллипс", "Крест"])
        params_layout.addWidget(self.struct_element_combo)
        
        params_layout.addWidget(QLabel("Размер ядра (нечетный):"))
        self.kernel_size_spin = QSpinBox()
        self.kernel_size_spin.setMinimum(3)
        self.kernel_size_spin.setMaximum(31)
        self.kernel_size_spin.setSingleStep(2)
        self.kernel_size_spin.setValue(5)
        params_layout.addWidget(self.kernel_size_spin)
        
        params_layout.addWidget(QLabel("Количество итераций:"))
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setMinimum(1)
        self.iterations_spin.setMaximum(10)
        self.iterations_spin.setValue(1)
        params_layout.addWidget(self.iterations_spin)
        
        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        operations_group = QGroupBox("Морфологические операции")
        operations_layout = QVBoxLayout()
        
        self.erosion_btn = QPushButton("Эрозия")
        self.erosion_btn.clicked.connect(self.apply_erosion)
        operations_layout.addWidget(self.erosion_btn)
        
        self.dilation_btn = QPushButton("Дилатация")
        self.dilation_btn.clicked.connect(self.apply_dilation)
        operations_layout.addWidget(self.dilation_btn)
        
        self.opening_btn = QPushButton("Размыкание")
        self.opening_btn.clicked.connect(self.apply_opening)
        operations_layout.addWidget(self.opening_btn)
        
        self.closing_btn = QPushButton("Замыкание")
        self.closing_btn.clicked.connect(self.apply_closing)
        operations_layout.addWidget(self.closing_btn)
        
        self.gradient_btn = QPushButton("Морфологический градиент")
        self.gradient_btn.clicked.connect(self.apply_gradient)
        operations_layout.addWidget(self.gradient_btn)
        
        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_image)
        operations_layout.addWidget(self.reset_btn)
        
        operations_group.setLayout(operations_layout)
        left_panel.addWidget(operations_group)
        
        left_panel.addStretch()
        
        right_panel = QVBoxLayout()
        
        self.original_label = QLabel("Оригинальное изображение")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(600, 400)
        self.original_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.original_label)
        
        self.processed_label = QLabel("Обработанное изображение")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(600, 400)
        self.processed_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.processed_label)
        
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.processed_image = self.original_image.copy()
                self.display_images()
    
    def get_kernel(self):
        """Возвращает структурирующий элемент для морфологических операций."""
        kernel_size = self.kernel_size_spin.value()
        element_type = self.struct_element_combo.currentText()
        
        if element_type == "Прямоугольник":
            return cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        elif element_type == "Эллипс":
            return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        elif element_type == "Крест":
            return cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size, kernel_size))
    
    def apply_erosion(self):
        if self.processed_image is not None:
            kernel = self.get_kernel()
            iterations = self.iterations_spin.value()
            self.processed_image = cv2.erode(
                self.processed_image, kernel, iterations=iterations
            )
            self.display_images()
    
    def apply_dilation(self):
        if self.processed_image is not None:
            kernel = self.get_kernel()
            iterations = self.iterations_spin.value()
            self.processed_image = cv2.dilate(
                self.processed_image, kernel, iterations=iterations
            )
            self.display_images()
    
    def apply_opening(self):
        if self.processed_image is not None:
            kernel = self.get_kernel()
            self.processed_image = cv2.morphologyEx(
                self.processed_image, cv2.MORPH_OPEN, kernel
            )
            self.display_images()
    
    def apply_closing(self):
        if self.processed_image is not None:
            kernel = self.get_kernel()
            self.processed_image = cv2.morphologyEx(
                self.processed_image, cv2.MORPH_CLOSE, kernel
            )
            self.display_images()
    
    def apply_gradient(self):
        if self.processed_image is not None:
            kernel = self.get_kernel()
            self.processed_image = cv2.morphologyEx(
                self.processed_image, cv2.MORPH_GRADIENT, kernel
            )
            self.display_images()
    
    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_images()
    
    def display_images(self):
        if self.original_image is not None:
            self._display_single_image(self.original_image, self.original_label)
        
        if self.processed_image is not None:
            self._display_single_image(self.processed_image, self.processed_label)

    def _display_single_image(self, image, label):
        if image.ndim == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)

        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        
        qimage = QImage(
            image_rgb.data, 
            w, h, bytes_per_line, 
            QImage.Format_RGB888
        )
        
        label.setPixmap(
            QPixmap.fromImage(qimage).scaled(
                label.width(),
                label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


# Повышение резкости

class SharpeningTab(QWidget):
    """
    Вкладка для повышения резкости изображений
    """
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.processed_image = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        left_panel = QVBoxLayout()
        
        load_group = QGroupBox("Загрузка изображения")
        load_layout = QVBoxLayout()
        self.load_btn = QPushButton("Загрузить изображение")
        self.load_btn.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_btn)
        load_group.setLayout(load_layout)
        left_panel.addWidget(load_group)
        
        params_group = QGroupBox("Параметры повышения резкости")
        params_layout = QVBoxLayout()
        
        params_layout.addWidget(QLabel("Метод повышения резкости:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Лапласиан", "Лапласиан Гауссиана (LoG)"])
        params_layout.addWidget(self.method_combo)
        
        params_layout.addWidget(QLabel("Размер ядра (ksize, нечетный):"))
        self.ksize_spin = QSpinBox()
        self.ksize_spin.setMinimum(1)
        self.ksize_spin.setMaximum(31)
        self.ksize_spin.setSingleStep(2)
        self.ksize_spin.setValue(3)
        params_layout.addWidget(self.ksize_spin)
        
        
        self.apply_btn = QPushButton("Применить резкость")
        self.apply_btn.clicked.connect(self.apply_sharpening) 
        params_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_image)
        params_layout.addWidget(self.reset_btn)

        params_group.setLayout(params_layout)
        left_panel.addWidget(params_group)
        
        left_panel.addStretch()
        
        right_panel = QVBoxLayout()
        
        self.original_label = QLabel("Оригинальное изображение")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setMinimumSize(600, 400)
        self.original_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.original_label)
        
        self.processed_label = QLabel("Обработанное изображение")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(600, 400)
        self.processed_label.setStyleSheet("border: 1px solid black;")
        right_panel.addWidget(self.processed_label)
        
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.processed_image = self.original_image.copy()
                self.display_images() 
                
    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_images()
    
    def apply_sharpening(self):
        """Применяет выбранный метод повышения резкости (Лаплас или LoG) с фиксированными параметрами."""
        if self.original_image is None:
            return
            
        method = self.method_combo.currentText()
        ksize = self.ksize_spin.value()
        
        sigma = 1.0  
        alpha = 1.0  

        img_float = self.original_image.astype(np.float64) / 255.0
        
        if len(self.original_image.shape) == 3:
            gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = self.original_image.copy()
            
        gray_float = gray_image.astype(np.float64) / 255.0


        if method == "Лапласиан":
            edge_mask = cv2.Laplacian(gray_float, cv2.CV_64F, ksize=ksize)
            
        elif method == "Лапласиан Гауссиана (LoG)":
            blur_ksize = ksize if ksize % 2 != 0 else ksize + 1
            if blur_ksize == 1: blur_ksize = 3
            
            blurred = cv2.GaussianBlur(gray_float, (blur_ksize, blur_ksize), sigma)
            edge_mask = cv2.Laplacian(blurred, cv2.CV_64F, ksize=1)
            
        else:
            self.processed_image = self.original_image.copy()
            self.display_images()
            return
                
        
        if len(self.original_image.shape) == 3:
            sharpened_b = img_float[:,:,0] - alpha * edge_mask
            sharpened_g = img_float[:,:,1] - alpha * edge_mask
            sharpened_r = img_float[:,:,2] - alpha * edge_mask
            
            sharpened_float = cv2.merge([sharpened_b, sharpened_g, sharpened_r])
        else:
            sharpened_float = gray_float - alpha * edge_mask

        sharpened_float = np.clip(sharpened_float, 0, 1)
        
        self.processed_image = (sharpened_float * 255).astype(np.uint8)
            
        self.display_images()
        
    def display_images(self):
        if self.original_image is not None:
            self._display_single_image(self.original_image, self.original_label)
        
        if self.processed_image is not None:
            self._display_single_image(self.processed_image, self.processed_label)

    def _display_single_image(self, image, label):
        if image is None:
            return

        if image.ndim == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = image_rgb.shape
            bytes_per_line = ch * w
            qimage = QImage(
                image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888
            )
        else:
            h, w = image.shape
            bytes_per_line = w
            qimage = QImage(
                image.data, w, h, bytes_per_line, QImage.Format_Grayscale8
            )
        
        label.setPixmap(
            QPixmap.fromImage(qimage).scaled(
                label.width(),
                label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

# Главное окно приложения

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Обработка изображений: Морфология и Повышение Резкости')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        self.tabs = QTabWidget()
        self.morphology_tab = MorphologyTab()
        self.sharpening_tab = SharpeningTab()
        
        self.tabs.addTab(self.morphology_tab, "Морфологическая обработка")
        self.tabs.addTab(self.sharpening_tab, "Повышение резкости")
        
        main_layout.addWidget(self.tabs)


def main():
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    
    screen_geometry = QApplication.primaryScreen().availableGeometry()
    window_geometry = window.frameGeometry()
    window.move((screen_geometry.width() - window_geometry.width()) // 2,
                 (screen_geometry.height() - window_geometry.height()) // 2)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()