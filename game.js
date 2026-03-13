// ─── ESTADO DEL JUEGO ─────────────────────────────────────
let ROWS = 9, COLS = 9, MINES = 10;
let board = [], revealed = [], flagged = [];
let gameOver = false, gameWon = false, firstClick = true;
let timerInterval = null, seconds = 0;
let minesLeft = MINES;
let paused = false;

// ─── DOM ──────────────────────────────────────────────────
const boardEl     = document.getElementById('board');
const mineCountEl = document.getElementById('mine-count');
const timerEl     = document.getElementById('timer');
const faceEl      = document.getElementById('face');
const resetBtn    = document.getElementById('reset-btn');
const overlay     = document.getElementById('overlay');
const overlayIcon = document.getElementById('overlay-icon');
const overlayMsg  = document.getElementById('overlay-msg');
const overlayBtn  = document.getElementById('overlay-btn');
const diffBtns    = document.querySelectorAll('.diff-btn');

// NUEVOS BOTONES
const howBtn   = document.getElementById('how-btn');
const hintBtn  = document.getElementById('hint-btn');
const pauseBtn = document.getElementById('pause-btn');


// ─── INICIALIZACIÓN ───────────────────────────────────────
function initGame() {

  clearInterval(timerInterval);

  seconds = 0;
  minesLeft = MINES;
  gameOver = false;
  gameWon = false;
  firstClick = true;
  paused = false;

  updateTimer();
  updateMineCount();

  faceEl.textContent = '😐';

  overlay.className = 'overlay';

  board    = Array(ROWS * COLS).fill(0);
  revealed = Array(ROWS * COLS).fill(false);
  flagged  = Array(ROWS * COLS).fill(false);

  renderBoard();
}


// ─── COLOCAR MINAS ────────────────────────────────────────
function placeMines(safeIdx) {

  let placed = 0;

  while (placed < MINES) {

    const idx = Math.floor(Math.random() * ROWS * COLS);

    if (board[idx] === -1 || idx === safeIdx) continue;

    board[idx] = -1;

    placed++;

  }

  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {

      const idx = r * COLS + c;

      if (board[idx] === -1) continue;

      board[idx] = countMinesAround(r, c);

    }
  }

}

function countMinesAround(r, c) {

  let count = 0;

  for (const [dr, dc] of neighbors()) {

    const nr = r + dr;
    const nc = c + dc;

    if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) {

      if (board[nr * COLS + nc] === -1) count++;

    }
  }

  return count;

}

function neighbors() {
  return [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];
}


// ─── RENDER TABLERO ───────────────────────────────────────
function renderBoard() {

  boardEl.style.gridTemplateColumns = `repeat(${COLS}, 30px)`;

  boardEl.innerHTML = '';

  for (let r = 0; r < ROWS; r++) {

    for (let c = 0; c < COLS; c++) {

      const idx = r * COLS + c;

      const cell = document.createElement('div');

      cell.className = 'cell';

      cell.dataset.idx = idx;

      if (revealed[idx]) {

        cell.classList.add('revealed');

        if (board[idx] === -1) {

          cell.classList.add('mine');

          cell.textContent = '💣';

        } else if (board[idx] > 0) {

          cell.classList.add(`n${board[idx]}`);

          cell.textContent = board[idx];

        }

      } else if (flagged[idx]) {

        cell.classList.add('flagged');

        cell.textContent = '🚩';

      }

      cell.addEventListener('click', () => handleClick(r, c));

      cell.addEventListener('contextmenu', (e) => {

        e.preventDefault();

        handleFlag(r, c);

      });

      // ─── SOPORTE MÓVIL (LONG PRESS) ─────────────────
      let pressTimer;

      cell.addEventListener("touchstart", () => {

        pressTimer = setTimeout(() => {

          handleFlag(r, c);

        }, 400);

      });

      cell.addEventListener("touchend", () => {

        clearTimeout(pressTimer);

      });

      boardEl.appendChild(cell);

    }

  }

}


// ─── ACTUALIZAR CELDA ─────────────────────────────────────
function updateCell(r, c) {

  const idx = r * COLS + c;

  const cell = boardEl.children[idx];

  if (!cell) return;

  cell.className = 'cell';

  cell.textContent = '';

  if (revealed[idx]) {

    cell.classList.add('revealed');

    if (board[idx] === -1) {

      cell.classList.add('mine');

      cell.textContent = '💣';

    } else if (board[idx] > 0) {

      cell.classList.add(`n${board[idx]}`);

      cell.textContent = board[idx];

    }

  } else if (flagged[idx]) {

    cell.classList.add('flagged');

    cell.textContent = '🚩';

  }

}


// ─── CLICK IZQUIERDO ──────────────────────────────────────
function handleClick(r, c) {

  if(paused) return;

  const idx = r * COLS + c;

  if (gameOver || gameWon || revealed[idx] || flagged[idx]) return;

  if (firstClick) {

    firstClick = false;

    placeMines(idx);

    startTimer();

    faceEl.textContent = '😮';

    setTimeout(() => {

      if (!gameOver && !gameWon)

      faceEl.textContent = '🙂';

    }, 200);

  }

  if (board[idx] === -1) {

    revealed[idx] = true;

    updateCell(r, c);

    triggerGameOver(r, c);

    return;

  }

  revealFlood(r, c);

  checkWin();

}


// ─── FLOOD FILL ───────────────────────────────────────────
function revealFlood(startR, startC) {

  const queue = [[startR, startC]];

  while (queue.length) {

    const [r, c] = queue.shift();

    const idx = r * COLS + c;

    if (revealed[idx] || flagged[idx]) continue;

    revealed[idx] = true;

    updateCell(r, c);

    if (board[idx] === 0) {

      for (const [dr, dc] of neighbors()) {

        const nr = r + dr;
        const nc = c + dc;

        if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !revealed[nr * COLS + nc]) {

          queue.push([nr, nc]);

        }

      }

    }

  }

}


// ─── BANDERA ──────────────────────────────────────────────
function handleFlag(r, c) {

  if(paused) return;

  const idx = r * COLS + c;

  if (gameOver || gameWon || revealed[idx]) return;

  flagged[idx] = !flagged[idx];

  minesLeft += flagged[idx] ? -1 : 1;

  updateMineCount();

  updateCell(r, c);

}


// ─── GAME OVER ────────────────────────────────────────────
function triggerGameOver() {

  gameOver = true;

  clearInterval(timerInterval);

  faceEl.textContent = '😵';

  for (let i = 0; i < board.length; i++) {

    if (board[i] === -1 && !flagged[i]) {

      revealed[i] = true;

    }

  }

  renderBoard();

  setTimeout(() => {

    overlayIcon.textContent = '💥';

    overlayMsg.textContent = 'GAME OVER';

    overlay.className = 'overlay show';

  }, 600);

}


// ─── VICTORIA ─────────────────────────────────────────────
function checkWin() {

  const unrevealed = revealed.filter(v => !v).length;

  if (unrevealed === MINES) {

    gameWon = true;

    clearInterval(timerInterval);

    faceEl.textContent = '😎';

    setTimeout(() => {

      overlayIcon.textContent = '🏆';

      overlayMsg.textContent = '¡VICTORIA!';

      overlay.className = 'overlay win show';

    }, 300);

  }

}


// ─── TIMER ─────────────────────────────────────────────────
function startTimer() {

  clearInterval(timerInterval);

  timerInterval = setInterval(() => {

    seconds = Math.min(seconds + 1, 999);

    updateTimer();

  }, 1000);

}

function updateTimer() {

  timerEl.textContent = String(seconds).padStart(3, '0');

}

function updateMineCount() {

  mineCountEl.textContent = String(Math.max(minesLeft, -99)).padStart(3, '0');

}


// ─── BOTÓN CÓMO JUGAR ─────────────────────────────────────
if(howBtn){

  howBtn.addEventListener("click", () => {

    alert(`OBJETIVO
Descubre todas las casillas sin minas.

CONTROLES
Click izquierdo → revelar
Click derecho → bandera 🚩

MÓVIL
Mantener presionado → bandera`);

  });

}


// ─── BOTÓN SUGERENCIA ─────────────────────────────────────
if(hintBtn){

  hintBtn.addEventListener("click", () => {

    if(gameOver || gameWon) return;

    let safe = [];

    for(let i=0;i<board.length;i++){

      if(board[i] !== -1 && !revealed[i]) safe.push(i);

    }

    if(!safe.length) return;

    const pick = safe[Math.floor(Math.random()*safe.length)];

    const cell = boardEl.children[pick];

    cell.style.boxShadow = "0 0 14px #39ff14";

    setTimeout(()=>{

      cell.style.boxShadow = "";

    },2000);

  });

}


// ─── BOTÓN PAUSA ──────────────────────────────────────────
if(pauseBtn){

  pauseBtn.addEventListener("click", () => {

    paused = !paused;

    if(paused){

      clearInterval(timerInterval);

      pauseBtn.textContent = "▶ CONTINUAR";

    }else{

      startTimer();

      pauseBtn.textContent = "⏸ PAUSA";

    }

  });

}


// ─── EVENTOS ──────────────────────────────────────────────
resetBtn.addEventListener('click', initGame);

overlayBtn.addEventListener('click', initGame);

diffBtns.forEach(btn => {

  btn.addEventListener('click', () => {

    diffBtns.forEach(b => b.classList.remove('active'));

    btn.classList.add('active');

    ROWS  = parseInt(btn.dataset.rows);
    COLS  = parseInt(btn.dataset.cols);
    MINES = parseInt(btn.dataset.mines);

    initGame();

  });

});


// ─── INICIAR ──────────────────────────────────────────────
initGame();