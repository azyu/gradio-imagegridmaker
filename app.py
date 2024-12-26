import gradio as gr
from PIL import Image
import math
import tempfile
import os

def combine_images(files, output_format, output_size, padding, spacing):
    if not files:
        return None, None

    try:
        # PIL 이미지로 변환
        images = [Image.open(file.name).convert("RGB") for file in files]

        num_images = len(images)
        grid_size = math.ceil(math.sqrt(num_images))

        # 행과 열 계산
        rows = math.ceil(num_images / grid_size)
        cols = grid_size

        # 원하는 출력 크기와 그리드의 패딩과 간격을 고려하여 각 이미지의 최대 크기 계산
        total_padding = 2 * padding + (cols - 1) * spacing
        max_width = (output_size - total_padding) // cols
        max_height = (output_size - total_padding) // rows

        resized_images = []
        for img in images:
            # 원본 비율 유지하며 이미지 리사이즈
            img_ratio = img.width / img.height
            target_ratio = max_width / max_height

            if img_ratio > target_ratio:
                new_width = max_width
                new_height = int(max_width / img_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * img_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)

            # 흰색 배경에 이미지 패딩
            new_img = Image.new("RGB", (max_width, max_height), (255, 255, 255))
            paste_x = (max_width - new_width) // 2
            paste_y = (max_height - new_height) // 2
            new_img.paste(img, (paste_x, paste_y))
            resized_images.append(new_img)

        # 결합된 이미지의 총 크기 계산
        combined_width = cols * max_width + (cols - 1) * spacing + 2 * padding
        combined_height = rows * max_height + (rows - 1) * spacing + 2 * padding

        # 흰색 배경의 새 이미지 생성
        combined_image = Image.new('RGB', (combined_width, combined_height), color=(255, 255, 255))

        for idx, img in enumerate(resized_images):
            row = idx // cols
            col = idx % cols
            x = padding + col * (max_width + spacing)
            y = padding + row * (max_height + spacing)
            combined_image.paste(img, (x, y))

        # 원하는 출력 크기로 리사이즈 (필요시)
        combined_image = combined_image.resize((output_size, output_size), Image.LANCZOS)

        # 이미지를 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix=f".{output_format.lower()}", delete=False) as tmp:
            combined_image.save(tmp, format=output_format)
            tmp_path = tmp.name

        return combined_image, tmp_path

    except Exception as e:
        # 예외 발생 시 메시지 반환 (이미지는 표시하지 않음)
        print(f"Error processing images: {e}")
        return None, None

with gr.Blocks() as iface:
    gr.Markdown("## 이미지 그리드 합치기")
    gr.Markdown("여러 이미지를 업로드하면 그리드 형태로 합쳐서 출력합니다. 이미지의 원본 비율을 유지하며, 남는 공간은 흰색으로 채워집니다.")

    with gr.Row():
        image_input = gr.File(
            label="이미지 업로드",
            file_count="multiple",
            file_types=["image"]  # 이미지 파일만 업로드 가능
        )

    with gr.Row():
        output_format = gr.Dropdown(
            label="출력 이미지 형식",
            choices=["PNG", "JPEG"],
            value="PNG"
        )
        output_size = gr.Dropdown(
            label="출력 이미지 크기",
            choices=[1024, 2048, 4096],
            value=1024
        )

    with gr.Row():
        padding = gr.Number(
            label="패딩 (픽셀)",
            value=10,
            precision=0
        )
        spacing = gr.Number(
            label="이미지 간격 (픽셀)",
            value=10,
            precision=0
        )

    combine_button = gr.Button("이미지 합치기")

    with gr.Row():
        output_image = gr.Image(
            label="합쳐진 이미지",
            type="pil"  # PIL 이미지 객체로 출력
        )
        output_file = gr.File(
            label="합쳐진 이미지 다운로드",
            file_types=["image"]
        )

    # 이미지 합치기 버튼 클릭 시 함수 호출
    combine_button.click(
        fn=combine_images,
        inputs=[image_input, output_format, output_size, padding, spacing],
        outputs=[output_image, output_file]
    )

if __name__ == "__main__":
    iface.launch()