from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import difflib
from docx import Document  # Для чтения Word-файлов (.docx)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_docx_file(file_bytes: bytes) -> str:
    """Читает текст из .docx файла."""
    try:
        import tempfile
        import os
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name
        
        # Читаем через python-docx
        doc = Document(tmp_file_path)
        paragraphs = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Игнорируем пустые строки
                paragraphs.append(paragraph.text)
        
        # Удаляем временный файл
        os.unlink(tmp_file_path)
        
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"Ошибка при чтении .docx: {e}")
        return ""

def read_text_file(file_bytes: bytes) -> str:
    """Читает текстовый файл с определением кодировки."""
    import chardet
    
    result = chardet.detect(file_bytes)
    encoding = result['encoding']
    confidence = result['confidence']
    
    print(f"Кодировка текста: {encoding}, уверенность: {confidence}")
    
    if encoding and confidence > 0.7:
        try:
            return file_bytes.decode(encoding, errors='replace')
        except:
            pass
    
    # Популярные кодировки для русского текста
    encodings_to_try = ['utf-8', 'windows-1251', 'cp1251', 'koi8-r', 'latin-1']
    for enc in encodings_to_try:
        try:
            return file_bytes.decode(enc, errors='replace')
        except:
            continue
    
    return file_bytes.decode('latin-1', errors='replace')

@app.post("/compare")
async def compare_files(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        print(f"\n=== Обработка файлов ===")
        print(f"Файл 1: {file1.filename}")
        print(f"Файл 2: {file2.filename}")
        
        # Читаем сырые байты
        file1_bytes = await file1.read()
        file2_bytes = await file2.read()
        
        print(f"Размер 1: {len(file1_bytes)} байт")
        print(f"Размер 2: {len(file2_bytes)} байт")
        
        # Определяем тип файла и читаем
        is_docx_1 = file1.filename.lower().endswith('.docx')
        is_docx_2 = file2.filename.lower().endswith('.docx')
        
        if is_docx_1:
            print("Читаю Файл 1 как .docx...")
            content1 = read_docx_file(file1_bytes)
        else:
            print("Читаю Файл 1 как текст...")
            content1 = read_text_file(file1_bytes)
        
        if is_docx_2:
            print("Читаю Файл 2 как .docx...")
            content2 = read_docx_file(file2_bytes)
        else:
            print("Читаю Файл 2 как текст...")
            content2 = read_text_file(file2_bytes)
        
        print(f"Файл 1: {len(content1)} символов")
        print(f"Файл 2: {len(content2)} символов")
        
        # Если файлы пустые
        if not content1 and not content2:
            return {"status": "success", "result": [], "message": "Оба файла пусты"}
        
        # Разбиваем на строки
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        print(f"Файл 1: {len(lines1)} строк")
        print(f"Файл 2: {len(lines2)} строк")
        
        # Сравниваем
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        result = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i1, i2):
                    result.append({
                        "left": lines1[k] if k < len(lines1) else "",
                        "right": lines2[j1 + (k - i1)] if (j1 + (k - i1)) < len(lines2) else "",
                        "status": "equal"
                    })
            elif tag == 'insert':
                for k in range(j1, j2):
                    result.append({
                        "left": "",
                        "right": lines2[k] if k < len(lines2) else "",
                        "status": "added"
                    })
            elif tag == 'delete':
                for k in range(i1, i2):
                    result.append({
                        "left": lines1[k] if k < len(lines1) else "",
                        "right": "",
                        "status": "deleted"
                    })
            elif tag == 'replace':
                for k in range(i2 - i1):
                    result.append({
                        "left": lines1[i1 + k] if i1 + k < len(lines1) else "",
                        "right": lines2[j1 + k] if j1 + k < len(lines2) else "",
                        "status": "changed"
                    })
        
        print(f"Сравнение завершено. Строк в результате: {len(result)}")
        return {"status": "success", "result": result, "message": "Файлы успешно сравнены"}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Ошибка при сравнении: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")