// 🐱 喵喵任務看板 Vue.js 應用
// Meow Meow Task Kanban Vue.js App

const { createApp, ref, computed, onMounted, watch } = Vue;

createApp({
  setup() {
    // ==================== 狀態 ====================
    
    // 認證狀態
    const isAuthenticated = ref(false);
    const username = ref('');
    const password = ref('');
    const loading = ref(false);
    const error = ref('');
    
    // 任務資料
    const tasks = ref([]);
    const stats = ref({ todo: 0, inprogress: 0, done: 0, error: 0, total: 0 });
    const syncing = ref(false);
    
    // UI 狀態
    const selectedTask = ref(null);
    const showAddTask = ref(false);
    const draggedTask = ref(null);
    
    // 新任務表單
    const newTask = ref({
      name: '',
      description: '',
      status: 'todo',
      type: 'manual'
    });
    
    // 看板欄位配置
    const columns = ref([
      { id: 'todo', name: '待辦', color: '#6b7280', tasks: [] },
      { id: 'inprogress', name: '進行中', color: '#3b82f6', tasks: [] },
      { id: 'done', name: '完成', color: '#22c55e', tasks: [] },
      { id: 'error', name: '錯誤', color: '#ef4444', tasks: [] }
    ]);
    
    // ==================== API 客戶端 ====================
    
    const apiBase = '/api';
    
    async function apiRequest(endpoint, options = {}) {
      const headers = {
        ...options.headers
      };
      
      if (username.value && password.value) {
        headers['Authorization'] = 'Basic ' + btoa(username.value + ':' + password.value);
      }
      
      const response = await fetch(apiBase + endpoint, {
        ...options,
        headers
      });
      
      if (response.status === 401) {
        error.value = '用戶名或密碼錯誤';
        loading.value = false;
        return null;
      }
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      return response.json();
    }
    
    // ==================== 任務操作 ====================
    
    async function loadTasks() {
      const data = await apiRequest('/tasks');
      if (data) {
        tasks.value = data;
        updateColumns();
        updateStats();
      }
    }
    
    async function loadStats() {
      const data = await apiRequest('/config');
      if (data && data.columns) {
        columns.value = data.columns.map(col => ({
          ...col,
          tasks: tasks.value.filter(t => t.status === col.id)
        }));
      }
      updateStats();
    }
    
    function updateColumns() {
      columns.value.forEach(col => {
        col.tasks = tasks.value.filter(t => t.status === col.id);
      });
    }
    
    function updateStats() {
      stats.value = {
        todo: tasks.value.filter(t => t.status === 'todo').length,
        inprogress: tasks.value.filter(t => t.status === 'inprogress').length,
        done: tasks.value.filter(t => t.status === 'done').length,
        error: tasks.value.filter(t => t.status === 'error').length,
        total: tasks.value.length
      };
    }
    
    async function createTask() {
      const data = await apiRequest('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask.value)
      });
      
      if (data) {
        showAddTask.value = false;
        newTask.value = { name: '', description: '', status: 'todo', type: 'manual' };
        await loadTasks();
      }
    }
    
    async function updateTask() {
      if (!selectedTask.value) return;
      
      await apiRequest(`/tasks/${selectedTask.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedTask.value)
      });
      
      await loadTasks();
    }
    
    async function deleteTask() {
      if (!selectedTask.value) return;
      
      if (!confirm('確定要刪除這個任務嗎？')) return;
      
      await apiRequest(`/tasks/${selectedTask.value.id}`, {
        method: 'DELETE'
      });
      
      selectedTask.value = null;
      await loadTasks();
    }
    
    async function moveTask(taskId, newStatus) {
      await apiRequest(`/tasks/${taskId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      
      await loadTasks();
    }
    
    // ==================== OpenClaw 同步 ====================
    
    async function syncOpenclaw() {
      syncing.value = true;
      try {
        await apiRequest('/sync', { method: 'POST' });
        await loadTasks();
      } finally {
        syncing.value = false;
      }
    }
    
    // ==================== 拖放操作 ====================
    
    function onDragStart(event, task) {
      draggedTask.value = task;
      event.dataTransfer.effectAllowed = 'move';
    }
    
    function onDrop(event, columnId) {
      if (draggedTask.value && draggedTask.value.status !== columnId) {
        moveTask(draggedTask.value.id, columnId);
      }
      draggedTask.value = null;
    }
    
    // ==================== 工具函數 ====================
    
    function getColumnIcon(status) {
      const icons = {
        todo: 'mdi-inbox-outline',
        inprogress: 'mdi-progress-clock',
        done: 'mdi-check-circle-outline',
        error: 'mdi-alert-circle-outline'
      };
      return icons[status] || 'mdi-help-circle-outline';
    }
    
    function truncate(text, length) {
      if (!text) return '';
      return text.length > length ? text.substring(0, length) + '...' : text;
    }
    
    function formatTime(isoString) {
      if (!isoString) return '';
      const date = new Date(isoString);
      const now = new Date();
      const diff = now - date;
      
      // 小於 1 小時
      if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return minutes <= 0 ? '剛剛' : `${minutes} 分鐘前`;
      }
      
      // 小於 24 小時
      if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} 小時前`;
      }
      
      // 其他
      return date.toLocaleDateString('zh-TW') + ' ' + 
             date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
    }
    
    // ==================== 認證 ====================
    
    async function login() {
      loading.value = true;
      error.value = '';
      
      try {
        const data = await apiRequest('/auth/verify', { method: 'POST' });
        
        if (data && data.success) {
          isAuthenticated.value = true;
          localStorage.setItem('kanban_auth', btoa(username.value + ':' + password.value));
          await loadTasks();
        }
      } catch (e) {
        error.value = '登入失敗，請檢查用戶名和密碼';
      } finally {
        loading.value = false;
      }
    }
    
    function logout() {
      isAuthenticated.value = false;
      username.value = '';
      password.value = '';
      tasks.value = [];
      localStorage.removeItem('kanban_auth');
    }
    
    // ==================== 生命週期 ====================
    
    onMounted(() => {
      // 檢查本地存儲的認證
      const storedAuth = localStorage.getItem('kanban_auth');
      if (storedAuth) {
        try {
          const decoded = atob(storedAuth);
          const [user, pass] = decoded.split(':');
          username.value = user;
          password.value = pass;
          login();
        } catch (e) {
          localStorage.removeItem('kanban_auth');
        }
      }
    });
    
    // ==================== 返回模板數據 ====================
    
    return {
      // 狀態
      isAuthenticated,
      username,
      password,
      loading,
      error,
      tasks,
      stats,
      syncing,
      selectedTask,
      showAddTask,
      newTask,
      columns,
      
      // 方法
      login,
      logout,
      loadTasks,
      refreshTasks: loadTasks,
      createTask,
      updateTask,
      deleteTask,
      syncOpenclaw,
      onDragStart,
      onDrop,
      showTaskDetail: (task) => { selectedTask.value = { ...task }; },
      
      // 工具
      getColumnIcon,
      truncate,
      formatTime
    };
  }
});
