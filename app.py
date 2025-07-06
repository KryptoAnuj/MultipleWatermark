import gradio as gr
from PIL import Image
import io

def tile_watermark(base_image, watermark, opacity=128, spacing_ratio=0.05, scale_ratio=0.1):
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')

    base_width, base_height = base_image.size
    new_wm_width = int(base_width * scale_ratio)
    aspect_ratio = watermark.height / watermark.width
    new_wm_height = int(new_wm_width * aspect_ratio)
    scaled_watermark = watermark.resize((new_wm_width, new_wm_height), Image.LANCZOS)

    alpha = scaled_watermark.split()[3]
    alpha = alpha.point(lambda p: p * opacity // 255)
    scaled_watermark.putalpha(alpha)

    spacing = int(base_width * spacing_ratio)

    tiled = Image.new('RGBA', base_image.size)
    for i, y in enumerate(range(0, base_height, scaled_watermark.height + spacing)):
        x_offset = (scaled_watermark.width + spacing) // 2 if i % 2 else 0
        for x in range(-x_offset, base_width, scaled_watermark.width + spacing):
            tiled.paste(scaled_watermark, (x, y), scaled_watermark)

    return Image.alpha_composite(base_image.convert('RGBA'), tiled).convert("RGB")

def process_images(image_files, watermark_image, opacity, spacing_ratio, scale_ratio):
    result_files = []
    for i, file in enumerate(image_files):
        with Image.open(file) as img:
            watermarked = tile_watermark(img, watermark_image, opacity, spacing_ratio, scale_ratio)
            img_bytes = io.BytesIO()
            watermarked.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            # Save temporarily
            filename = f"watermarked_{i+1}.jpg"
            with open(filename, "wb") as f:
                f.write(img_bytes.read())
            result_files.append(filename)
    return result_files

iface = gr.Interface(
    fn=process_images,
    inputs=[
        gr.File(file_types=["image"], label="Upload Multiple Images", file_count="multiple"),
        gr.Image(type="pil", label="Watermark Image"),
        gr.Slider(0, 255, step=1, value=128, label="Opacity"),
        gr.Slider(0.01, 0.2, step=0.01, value=0.05, label="Spacing Ratio"),
        gr.Slider(0.05, 0.3, step=0.01, value=0.1, label="Scale Ratio"),
    ],
    outputs=gr.Files(label="Download JPGs"),
    title="Watermark Tool",
    description="Upload multiple images + watermark. Download watermarked images in JPG format.",
)

iface.launch()
