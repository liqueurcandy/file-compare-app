<script setup>
import { ref } from 'vue';

const file1 = ref(null);
const file2 = ref(null);
const compareResult = ref([]);
const loading = ref(false);
const error = ref('');
const file1Name = ref('');
const file2Name = ref('');

const handleFile1 = (event) => {
  file1.value = event.target.files[0];
  file1Name.value = file1.value.name;
  reset();
};

const handleFile2 = (event) => {
  file2.value = event.target.files[0];
  file2Name.value = file2.value.name;
  reset();
};

const reset = () => {
  compareResult.value = [];
  error.value = '';
};

const compareFiles = async () => {
  if (!file1.value || !file2.value) {
    error.value = 'Пожалуйста, выберите оба файла!';
    return;
  }

  loading.value = true;
  error.value = '';
  
  const formData = new FormData();
  formData.append('file1', file1.value);
  formData.append('file2', file2.value);

  try {
    const response = await fetch('http://localhost:8000/compare', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Ошибка сервера');
    }
    
    const data = await response.json();
    
    if (data.status === 'success') {
      compareResult.value = data.result;
    } else {
      error.value = data.message || 'Ошибка при сравнении';
    }
  } catch (err) {
    console.error(err);
    error.value = err.message || 'Не удалось подключиться к серверу. Убедитесь, что Python скрипт запущен.';
  } finally {
    loading.value = false;
  }
};

// Эта функция была пропущена и вызывала ошибку
const getLineClass = (row, side) => {
  if (row.status === 'equal') return 'equal';
  
  if (side === 'left') {
    if (row.status === 'deleted') return 'deleted';
    if (row.status === 'changed') return 'changed'; // Измененная строка в левом файле
    if (row.status === 'added') return 'hidden';   // Ничего не должно быть, но на всякий случай
  }
  
  if (side === 'right') {
    if (row.status === 'added') return 'added';
    if (row.status === 'changed') return 'changed'; // Измененная строка в правом файле
    if (row.status === 'deleted') return 'hidden';  // Ничего не должно быть
  }
  
  return '';
};
</script>

<template>
  <div class="app">
    <header>
      <h1>Сравнение файлов</h1>
      <p>Загрузите два файла для параллельного просмотра различий</p>
    </header>

    <!-- Панель загрузки -->
    <div class="upload-panel">
      <div class="file-input">
        <label>Файл 1 (Оригинал)</label>
        <input type="file" @change="handleFile1" accept=".txt,.md,.py,.js,.json,.csv,.log" />
        <span class="file-name">{{ file1Name }}</span>
      </div>
      
      <div class="file-input">
        <label>Файл 2 (Изменения)</label>
        <input type="file" @change="handleFile2" accept=".txt,.md,.py,.js,.json,.csv,.log" />
        <span class="file-name">{{ file2Name }}</span>
      </div>

      <button @click="compareFiles" :disabled="loading" class="btn-compare">
        {{ loading ? 'Обработка...' : 'Сравнить файлы' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <!-- Результат сравнения -->
    <div v-if="compareResult.length > 0" class="comparison">
      <div class="file-tabs">
        <div class="tab left">Файл 1: {{ file1Name }}</div>
        <div class="tab right">Файл 2: {{ file2Name }}</div>
      </div>
      
      <div class="compare-container">
        <div class="col left-col">
          <div class="line-numbers">
            <div v-for="(row, i) in compareResult" :key="'ln' + i" class="ln">{{ i + 1 }}</div>
          </div>
          <div class="lines">
            <div 
              v-for="(row, i) in compareResult" 
              :key="'left' + i" 
              class="line"
              :class="getLineClass(row, 'left')"
            >
              {{ row.left }}
            </div>
          </div>
        </div>
        
        <div class="divider"></div>
        
        <div class="col right-col">
          <div class="line-numbers">
            <div v-for="(row, i) in compareResult" :key="'rn' + i" class="ln">{{ i + 1 }}</div>
          </div>
          <div class="lines">
            <div 
              v-for="(row, i) in compareResult" 
              :key="'right' + i" 
              class="line"
              :class="getLineClass(row, 'right')"
            >
              {{ row.right }}
            </div>
          </div>
        </div>
      </div>

      <!-- Легенда -->
      <div class="legend">
        <div class="legend-item">
          <div class="color-box equal"></div>
          <span>Совпадают</span>
        </div>
        <div class="legend-item">
          <div class="color-box deleted"></div>
          <span>Удалено (файл 1)</span>
        </div>
        <div class="legend-item">
          <div class="color-box added"></div>
          <span>Добавлено (файл 2)</span>
        </div>
        <div class="legend-item">
          <div class="color-box changed"></div>
          <span>Изменено</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

header p {
  color: #666;
}

/* Панель загрузки */
.upload-panel {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  align-items: flex-end;
}

.file-input {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  min-width: 200px;
}

.file-input label {
  font-weight: 600;
  color: #2c3e50;
}

.file-input input[type="file"] {
  padding: 10px;
  border: 2px dashed #ddd;
  border-radius: 4px;
  cursor: pointer;
  background: #f9f9f9;
  transition: border-color 0.3s;
  width: 100%;
  box-sizing: border-box;
}

.file-input input[type="file"]:hover {
  border-color: #3498db;
}

.file-name {
  font-size: 0.9rem;
  color: #666;
  background: #eef;
  padding: 5px 10px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.btn-compare {
  padding: 10px 25px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  height: 45px;
}

.btn-compare:hover:not(:disabled) {
  background: #27ae60;
}

.btn-compare:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.error {
  background: #fee;
  color: #c0392b;
  padding: 15px;
  border-radius: 5px;
  border: 1px solid #e74c3c;
  margin-bottom: 20px;
}

/* Стили сравнения */
.comparison {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.file-tabs {
  display: flex;
  background: #34495e;
  color: white;
}

.tab {
  flex: 1;
  padding: 12px 15px;
  text-align: center;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab.left { border-right: 1px solid #2c3e50; }

.compare-container {
  display: flex;
  border-top: 1px solid #ddd;
  height: 500px;
  overflow: hidden;
}

.col {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-col {
  background: #fafafa;
}

.right-col {
  background: #fff;
}

.divider {
  width: 2px;
  background: #ccc;
  cursor: col-resize;
}

.line-numbers {
  background: #e8e8e8;
  padding: 10px 5px;
  text-align: right;
  color: #999;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  border-right: 1px solid #ddd;
  overflow: hidden;
  min-width: 40px;
  user-select: none;
}

.ln {
  line-height: 20px;
  height: 20px;
}

.lines {
  flex: 1;
  padding: 10px 5px;
  overflow: auto;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  white-space: pre;
  tab-size: 4;
  line-height: 20px; /* Фиксируем высоту строки */
}

.line {
  height: 20px;
  padding: 0 5px;
  white-space: pre;
  overflow: hidden;
}

/* Подсветка статусов */
.line.equal {
  color: #333;
  background: transparent;
}

.line.deleted {
  background: #ffebee; /* Светло-красный */
  color: #c62828;
  text-decoration: line-through;
}

.line.added {
  background: #e8f5e9; /* Светло-зеленый */
  color: #2e7d32;
}

.line.changed {
  background: #fff3e0; /* Светло-оранжевый */
  color: #e65100;
}

.line.hidden {
  background: transparent;
  color: transparent; /* Прозрачный текст */
}

/* Левая колонка */
.left-col .line.deleted {
  border-left: 3px solid #c62828;
}

.left-col .line.changed {
  border-left: 3px solid #e65100;
}

/* Правая колонка */
.right-col .line.added {
  border-left: 3px solid #27ae60;
}

.right-col .line.changed {
  border-left: 3px solid #e65100;
}

/* Легенда */
.legend {
  display: flex;
  gap: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #ddd;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #555;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  border: 1px solid #ddd;
}

.color-box.equal { background: #f9f9f9; }
.color-box.deleted { background: #ffebee; }
.color-box.added { background: #e8f5e9; }
.color-box.changed { background: #fff3e0; }
</style>