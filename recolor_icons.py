import os
import colorsys
from PIL import Image, ImageColor, ImageFilter, UnidentifiedImageError # <-- ImageFilter 新增

def hex_to_rgba(hex_color):
    """将 HEX 颜色字符串转换为 RGBA 元组 (0-255)。"""
    try:
        rgb = ImageColor.getrgb(hex_color)
        return rgb + (255,) # 添加完全不透明的 alpha
    except ValueError:
        raise ValueError(f"无效的 HEX 颜色代码: {hex_color}")

def recolor_icon_minimalist(image_path, output_path, target_color_rgba, threshold=128, blur_radius=0):
    """
    读取图标，应用模糊（可选），然后进行阈值处理以创建极简风格。
    亮部使用目标颜色，暗部透明，保留原始轮廓的 alpha。
    """
    try:
        # 打开图像并确保是 RGBA 模式
        img = Image.open(image_path).convert("RGBA")
        original_alpha = img.getchannel('A') # 保存原始 alpha 通道

        # --- 1. 转换为灰度图 ---
        img_gray = img.convert('L')

        # --- 2. (可选) 应用高斯模糊 ---
        if blur_radius > 0:
            img_gray = img_gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            print(f"  应用高斯模糊, 半径: {blur_radius}")

        # --- 3. 阈值处理 ---
        img_threshold = img_gray.point(lambda p: 255 if p > threshold else 0, mode='1')
        # mode='1' 产生一个只有黑(0)白(255)的二值图像
        # 白色部分代表原始图像中亮度高于阈值的区域

        # --- 4. 创建新的彩色图像 ---
        # 创建一个完全透明的背景
        new_img = Image.new('RGBA', img.size, (0, 0, 0, 0))

        # 创建一个目标颜色的图层 (只含 RGB，忽略 alpha)
        # 我们将使用原始 alpha 和阈值结果作为蒙版
        color_layer = Image.new('RGB', img.size, target_color_rgba[:3])

        # --- 5. 合成最终图像 ---
        # 关键：蒙版需要结合原始 alpha 和阈值结果
        # 我们希望只在原始图像不透明 *且* 亮度高于阈值的区域应用目标色

        # 将阈值图像 (mode '1') 转换为 'L' 模式，以便用作蒙版
        # 白色 (255) 区域将被着色，黑色 (0) 区域将保持透明
        threshold_mask_L = img_threshold.convert('L')

        # 将原始 alpha 通道 ('L' 模式) 与阈值蒙版 ('L' 模式) 结合
        # 使用 point 实现逐像素的 "与" 操作：只有当两者都 > 0 时，结果才 > 0
        # 这里我们取两者中的最小值，效果等同于逻辑与 (因为阈值蒙版只有 0 和 255)
        # 最终蒙版：原始图像不透明且亮度高于阈值的区域为白色(或灰色)，其余为黑色
        final_mask = Image.blend(threshold_mask_L, original_alpha.point(lambda p: 255 if p > 0 else 0), 0.0) # 不透明区域转为255
        # 更精确的结合方式：
        final_mask_data = []
        threshold_data = threshold_mask_L.getdata()
        alpha_data = original_alpha.getdata()
        for i in range(len(alpha_data)):
            # 只有当原始 alpha > 0 且 阈值判断为前景(255) 时，才应用颜色
            # 并且最终的 alpha 取决于原始 alpha
            if alpha_data[i] > 0 and threshold_data[i] == 255:
                final_mask_data.append(alpha_data[i]) # 使用原始 alpha 实现抗锯齿
            else:
                final_mask_data.append(0) # 其他区域完全透明

        final_mask_image = Image.new('L', img.size)
        final_mask_image.putdata(final_mask_data)


        # 将目标色图层粘贴到透明背景上，使用最终计算出的蒙版
        new_img.paste(color_layer, (0, 0), mask=final_mask_image) # 使用精细蒙版

        # 保存为 PNG 格式
        new_img.save(output_path, format='PNG')
        print(f"处理完成 (极简): {os.path.basename(image_path)} -> {os.path.basename(output_path)}")

    except UnidentifiedImageError:
        print(f"跳过非图像或无法识别的文件: {os.path.basename(image_path)}")
    except Exception as e:
        print(f"处理文件 {os.path.basename(image_path)} 时出错: {e}")
        # import traceback # 取消注释以查看详细错误
        # traceback.print_exc()

def main():
    # --- 配置 ---
    input_directory = r"D:\GitHubRepos\recolor-app-icons\input"
    output_directory = r"D:\GitHubRepos\recolor-app-icons\output"
    target_hex_color = "#73dee3"
    threshold_value = 130  # 亮度阈值 (0-255)，可以调整这个值！ 128是中间值，较低的值会包含更多暗部
    blur_radius = 1      # 高斯模糊半径 (0表示不模糊)，可以调整这个值！ 1 或 2 通常能提供不错的简化效果
    # -------------

    # 验证并获取目标颜色的 RGBA 值
    try:
        target_color_rgba = hex_to_rgba(target_hex_color)
        print(f"目标颜色: {target_hex_color} -> RGBA: {target_color_rgba}")
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
    print(f"亮度阈值: {threshold_value}")
    print(f"高斯模糊半径: {blur_radius}")

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
                    # 调用新的处理函数
                    recolor_icon_minimalist(input_path, output_path, target_color_rgba, threshold_value, blur_radius)
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