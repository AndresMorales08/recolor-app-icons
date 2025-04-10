import os
import colorsys
from PIL import Image, ImageColor, ImageFilter, UnidentifiedImageError # ImageFilter is needed
import math

# --- Helper Functions (hex_to_rgb_normalized, rgb_normalized_to_rgba_int, hex_to_rgba) ---
# (These functions remain the same as in the previous 'posterize' script)
def hex_to_rgb_normalized(hex_color):
    """将 HEX 颜色字符串转换为归一化的 RGB 元组 (0.0-1.0)。"""
    try:
        rgb_int = ImageColor.getrgb(hex_color)
        return tuple(c / 255.0 for c in rgb_int)
    except ValueError:
        raise ValueError(f"无效的 HEX 颜色代码: {hex_color}")

def rgb_normalized_to_rgba_int(rgb_norm, alpha=255):
    """将归一化的 RGB (0.0-1.0) 转换为整数 RGBA (0-255)。"""
    r = min(255, max(0, int(rgb_norm[0] * 255 + 0.5)))
    g = min(255, max(0, int(rgb_norm[1] * 255 + 0.5)))
    b = min(255, max(0, int(rgb_norm[2] * 255 + 0.5)))
    return (r, g, b, alpha)

def hex_to_rgba(hex_color):
    """将 HEX 颜色字符串转换为 RGBA 元组 (0-255)。"""
    try:
        rgb = ImageColor.getrgb(hex_color)
        return rgb + (255,) # 添加完全不透明的 alpha
    except ValueError:
        raise ValueError(f"无效的 HEX 颜色代码: {hex_color}")
# ------------------------------------------------------------------------------

def generate_palette(base_hex, num_colors=3):
    """
    基于基础 HEX 颜色，生成一个包含 num_colors 种颜色的调色板 (RGBA 整数元组列表)，
    通过调整亮度生成，从暗到亮排序。
    (This function remains the same as in the previous 'posterize' script)
    """
    if num_colors < 2:
        num_colors = 2

    try:
        base_rgb_norm = hex_to_rgb_normalized(base_hex)
        base_h, base_l, base_s = colorsys.rgb_to_hls(*base_rgb_norm)
        print(f"基础颜色 HLS: (H={base_h:.3f}, L={base_l:.3f}, S={base_s:.3f})")

        palette_rgba = []
        min_l = 0.25
        max_l = 0.85

        if num_colors == 1:
            lightness_levels = [base_l]
        else:
             lightness_levels = [min_l + (max_l - min_l) * i / (num_colors - 1) for i in range(num_colors)]

        closest_idx = min(range(num_colors), key=lambda i: abs(lightness_levels[i] - base_l))
        lightness_levels[closest_idx] = base_l
        lightness_levels.sort()

        print(f"生成的亮度级别: {[f'{l:.3f}' for l in lightness_levels]}")

        for l in lightness_levels:
            l_clamped = max(0.0, min(1.0, l))
            # s_adjusted = base_s * (1 - abs(l_clamped - 0.5) * 0.5) # 保持原始饱和度可能更好
            # s_adjusted = max(0.0, min(1.0, s_adjusted))
            new_rgb_norm = colorsys.hls_to_rgb(base_h, l_clamped, base_s)
            palette_rgba.append(rgb_normalized_to_rgba_int(new_rgb_norm))

        print("生成的调色板 (RGBA):")
        for i, color in enumerate(palette_rgba):
            print(f"  Level {i}: {color}")
        return palette_rgba

    except Exception as e:
        print(f"生成调色板时出错: {e}")
        try:
            base_rgba = hex_to_rgba(base_hex)
            return [base_rgba]
        except:
            raise ValueError("无法生成调色板且无法获取基础色")


# --- MODIFIED FUNCTION ---
def recolor_icon_posterize_blur(image_path, output_path, palette, blur_radius=0.8):
    """
    读取图标，应用高斯模糊（如果 blur_radius > 0），
    然后将其颜色量化到提供的调色板，保留原始 alpha。
    """
    try:
        num_colors = len(palette)
        if num_colors == 0:
            print("错误：调色板为空！")
            return

        # 打开图像并确保是 RGBA 模式
        img = Image.open(image_path).convert("RGBA")
        original_alpha = img.getchannel('A') # 保存原始 alpha 通道

        # 转换为灰度图以获取亮度
        img_gray = img.convert('L')

        # --- >>> 新增：应用高斯模糊 <<< ---
        if blur_radius > 0:
            img_gray = img_gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            print(f"  应用高斯模糊, 半径: {blur_radius:.2f}")
        # --- >>> 模糊结束 <<< ---

        # 获取（可能已模糊的）灰度数据和原始 Alpha 数据
        gray_data = img_gray.getdata()
        alpha_data = original_alpha.getdata()

        new_data = []
        # 计算亮度阈值
        thresholds = [(i + 1) * 256 / num_colors for i in range(num_colors - 1)]

        for i in range(len(gray_data)):
            gray_value = gray_data[i]
            alpha_value = alpha_data[i]

            if alpha_value > 0:
                # 确定颜色区间
                color_index = 0
                for threshold in thresholds:
                    if gray_value > threshold:
                        color_index += 1
                    else:
                        break

                chosen_color_rgb = palette[color_index][:3]
                new_data.append(chosen_color_rgb + (alpha_value,))
            else:
                new_data.append((0, 0, 0, 0))

        # 创建新图像并填充处理后的像素数据
        new_img = Image.new("RGBA", img.size)
        new_img.putdata(new_data)

        # 保存为 PNG 格式
        new_img.save(output_path, format='PNG')
        print(f"处理完成 (Blurred Posterize): {os.path.basename(image_path)} -> {os.path.basename(output_path)}")

    except UnidentifiedImageError:
        print(f"跳过非图像或无法识别的文件: {os.path.basename(image_path)}")
    except Exception as e:
        print(f"处理文件 {os.path.basename(image_path)} 时出错: {e}")
        import traceback
        traceback.print_exc()
# --- END OF MODIFIED FUNCTION ---

def main():
    # --- 配置 ---
    input_directory = r"D:\GitHubRepos\recolor-app-icons\input"
    output_directory = r"D:\GitHubRepos\recolor-app-icons\output"
    target_hex_color = "#73dee3"
    number_of_colors = 3  # 调色板中的颜色数量
    blur_radius = 0.8     # <<< 高斯模糊半径 (0 表示不模糊, 建议 0.5 - 1.5 之间)
    # -------------

    # 生成调色板
    try:
        palette = generate_palette(target_hex_color, number_of_colors)
        if not palette:
            print("错误：无法生成调色板。")
            return
    except ValueError as e:
        print(f"错误: {e}")
        return

    # 检查输入目录是否存在
    if not os.path.isdir(input_directory):
        print(f"错误：输入目录不存在: {input_directory}")
        return

    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)
    print(f"输入目录: {input_directory}")
    print(f"输出目录: {output_directory}")
    print(f"使用的颜色数: {len(palette)}")
    print(f"高斯模糊半径: {blur_radius if blur_radius > 0 else '无'}") # 打印模糊设置

    # 遍历输入目录
    count = 0
    processed_count = 0
    skipped_count = 0
    error_count = 0

    print("\n开始处理文件...")
    for filename in os.listdir(input_directory):
        if filename.lower().endswith(".webp"):
            count += 1
            input_path = os.path.join(input_directory, filename)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_directory, output_filename)

            if os.path.isfile(input_path):
                try:
                    # 调用修改后的处理函数，传入模糊半径
                    recolor_icon_posterize_blur(input_path, output_path, palette, blur_radius)
                    processed_count += 1
                except Exception as e:
                    error_count += 1
            else:
                print(f"跳过，不是文件: {filename}")
                skipped_count += 1
        # else:
            # print(f"跳过非 .webp 文件: {filename}")
            # skipped_count += 1

    print("\n--- 处理结果 ---")
    if count == 0:
        print("在输入目录中未找到 .webp 文件。")
    else:
        print(f"共找到 {count} 个 .webp 文件。")
        print(f"成功处理: {processed_count} 个")
        if skipped_count > 0:
            print(f"跳过 (非文件或非webp): {skipped_count} 个")
        if error_count > 0:
            print(f"处理时发生错误: {error_count} 个")
        print(f"重新着色的图标已保存到: {output_directory}")

if __name__ == "__main__":
    # 确保已安装 Pillow: pip install Pillow
    main()