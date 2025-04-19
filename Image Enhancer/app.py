import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import cv2
import numpy as np

class ImageEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Image Enhancer")
        self.root.geometry("1000x800")
        self.root.config(bg="#181818")  # Dark background

        self.image = None
        self.enhanced_image = None
        self.tk_image = None
        self.history = []

        self.setup_home_page()

    def setup_home_page(self):
        # Frame to contain scrollable content
        home_frame = ttk.Frame(self.root, padding=10)
        home_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas widget and a vertical scrollbar
        canvas_frame = ttk.Frame(home_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#181818", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a window inside the canvas to hold content (Home Page)
        self.canvas_window_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.canvas_window_frame, anchor="nw")

        title_label = ttk.Label(self.canvas_window_frame, text="Welcome to Image Enhancer!", font=('Helvetica', 24, 'bold'), foreground="#ffffff")
        title_label.pack(pady=50)

        # Buttons to navigate to the image enhancement page
        upload_button = ttk.Button(self.canvas_window_frame, text="Start Enhancing Images", command=self.setup_image_enhancement_page, width=20, style="TButton")
        upload_button.pack(pady=20)

        # Update scrollable region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def setup_image_enhancement_page(self):
        # Clear home page and set up image enhancement page
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create image enhancement UI
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 12, 'bold'), relief="flat", background="#e50914", foreground="white")
        style.map("TButton", background=[('active', '#f40612')])  # Hover effect (Netflix red)
        style.configure("TLabel", font=('Helvetica', 12, 'bold'), background="#181818", foreground="#ffffff")

        # Frame for scrollable content
        main_frame = ttk.Frame(self.root, padding=10, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for displaying widgets
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#181818", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a window inside the canvas to hold content (Image Enhancement page)
        self.canvas_window_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.canvas_window_frame, anchor="nw")

        # Upload Section
        top_frame = ttk.Frame(self.canvas_window_frame)
        top_frame.pack(pady=20)
        ttk.Label(top_frame, text="📤 Upload Your Image", font=('Helvetica', 16, 'bold')).pack()
        ttk.Button(top_frame, text="Upload Image", command=self.upload_image).pack(pady=5)

        # Canvas to display image
        img_frame = ttk.Frame(self.canvas_window_frame)
        img_frame.pack(pady=20)
        self.canvas_image = tk.Canvas(img_frame, width=600, height=400, bg="#333333", relief=tk.SUNKEN, bd=2)
        self.canvas_image.pack()

        # Sliders
        slider_section = ttk.LabelFrame(self.canvas_window_frame, text="🔧 Adjustments", padding=10)
        slider_section.pack(pady=20, fill=tk.X, padx=10)
        self.create_slider(slider_section, "Brightness", 0.1, 2.0, 1.0)
        self.create_slider(slider_section, "Contrast", 0.1, 2.0, 1.0)
        self.create_slider(slider_section, "Sharpness", 0.1, 2.0, 1.0)
        self.create_slider(slider_section, "Color", 0.1, 2.0, 1.0)

        # Filters
        filter_section = ttk.LabelFrame(self.canvas_window_frame, text="🎨 Filters & Effects", padding=10)
        filter_section.pack(pady=20, fill=tk.X, padx=10)
        for text, cmd in [
            ("Grayscale", self.apply_grayscale),
            ("Sepia", self.apply_sepia),
            ("Blur", self.apply_blur),
            ("Edge", self.apply_edge),
            ("Cartoon", self.apply_cartoon),
            ("Sketch", self.apply_sketch),
            ("Undo", self.undo),
            ("AI Upscale (Coming Soon)", self.upscale_info)
        ]:
            ttk.Button(filter_section, text=text, command=cmd, style="TButton").pack(side=tk.LEFT, padx=6, pady=5)

        # Save
        save_frame = ttk.Frame(self.canvas_window_frame)
        save_frame.pack(pady=20)
        ttk.Button(save_frame, text="💾 Save Enhanced Image", command=self.save_image, style="TButton").pack()

        # Update scrollable region
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_slider(self, parent, label, from_, to, init):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10, padx=10)
        ttk.Label(frame, text=label, width=15, foreground="#ffffff").pack(side=tk.LEFT)
        slider = ttk.Scale(frame, from_=from_, to=to, value=init, orient=tk.HORIZONTAL,
                           command=lambda e: self.update_image())
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        setattr(self, f"{label.lower()}_slider", slider)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            self.image = Image.open(file_path).convert("RGB")
            self.enhanced_image = self.image.copy()
            self.history.clear()
            self.display_image(self.image)

    def update_image(self):
        if self.image:
            self.history.append(self.enhanced_image.copy())
            img = self.image.copy()
            img = ImageEnhance.Brightness(img).enhance(self.brightness_slider.get())
            img = ImageEnhance.Contrast(img).enhance(self.contrast_slider.get())
            img = ImageEnhance.Sharpness(img).enhance(self.sharpness_slider.get())
            img = ImageEnhance.Color(img).enhance(self.color_slider.get())
            self.enhanced_image = img
            self.display_image(img)

    def display_image(self, img):
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS
        img = img.resize((600, 400), resample)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas_image.delete("all")
        self.canvas_image.create_image(300, 200, image=self.tk_image)

    def save_image(self):
        if self.enhanced_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                self.enhanced_image.save(file_path)

    def undo(self):
        if self.history:
            self.enhanced_image = self.history.pop()
            self.display_image(self.enhanced_image)

    def apply_grayscale(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            img = self.enhanced_image.convert("L").convert("RGB")
            self.enhanced_image = img
            self.display_image(img)

    def apply_sepia(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            img = self.enhanced_image.convert("RGB")
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = img.getpixel((x, y))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
            self.enhanced_image = img
            self.display_image(img)

    def apply_blur(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            blurred = self.enhanced_image.filter(ImageFilter.GaussianBlur(2))
            self.enhanced_image = blurred
            self.display_image(blurred)

    def apply_edge(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            edged = self.enhanced_image.filter(ImageFilter.FIND_EDGES)
            self.enhanced_image = edged
            self.display_image(edged)

    def apply_cartoon(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            img = np.array(self.enhanced_image)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255,
                                          cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 9, 9)
            color = cv2.bilateralFilter(img, 9, 250, 250)
            cartoon = cv2.bitwise_and(color, color, mask=edges)
            cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
            cartoon_img = Image.fromarray(cartoon_rgb)
            self.enhanced_image = cartoon_img
            self.display_image(cartoon_img)

    def apply_sketch(self):
        if self.enhanced_image:
            self.history.append(self.enhanced_image.copy())
            img = np.array(self.enhanced_image)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            gray, sketch = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
            sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_BGR2RGB)
            sketch_img = Image.fromarray(sketch_rgb)
            self.enhanced_image = sketch_img
            self.display_image(sketch_img)

    def upscale_info(self):
        messagebox.showinfo("AI Upscale", "AI Upscaling is under development.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancerApp(root)
    root.mainloop()
