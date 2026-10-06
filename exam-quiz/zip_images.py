import zipfile, os, sys
sys.stdout.reconfigure(encoding='utf-8')

img_dir = r'D:\应用程序开发\刷题\question_images'
zip_path = r'D:\应用程序开发\刷题\题目配图_已提取262题.zip'

count = 0
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(img_dir):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, img_dir)
                zf.write(file_path, arcname)
                count += 1

print(f'打包完成: {zip_path}')
print(f'包含图片数: {count}张')
