/**
 * main.js - Khởi tạo bàn cờ Chess AI
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM đã sẵn sàng. Đang khởi tạo...");

    // 1. Kiểm tra thư viện
    if (typeof Chess === 'undefined') {
        console.error("LỖI: Không tìm thấy thư viện chess.js!");
        document.getElementById('status').innerText = "LỖI: Không tìm thấy chess.js";
        return;
    }
    if (typeof Chessground === 'undefined') {
        console.error("LỖI: Không tìm thấy thư viện Chessground!");
        document.getElementById('status').innerText = "LỖI: Không tìm thấy Chessground";
        return;
    }

    // 2. Khởi tạo logic game
    const game = new Chess();
    let board = null;

    // Hàm lấy danh sách nước đi hợp lệ cho Chessground
    function getValidMoves() {
        const dests = new Map();
        game.SQUARES.forEach(s => {
            const ms = game.moves({ square: s, verbose: true });
            if (ms.length) dests.set(s, ms.map(m => m.to));
        });
        return dests;
    }

    // Xử lý khi di chuyển quân trên bàn cờ
    function onMove(orig, dest) {
        const move = game.move({ from: orig, to: dest, promotion: 'q' });
        if (move === null) {
            board.set({ fen: game.fen() });
            return;
        }
        updateBoardStatus();
    }

    // Cập nhật trạng thái chữ và lượt đi
    function updateBoardStatus() {
        const statusEl = document.getElementById('status');
        let statusText = game.turn() === 'w' ? 'Lượt đi: Trắng' : 'Lượt đi: Đen';

        if (game.in_checkmate()) statusText = 'Chiếu bí! ' + (game.turn() === 'w' ? 'Đen thắng' : 'Trắng thắng');
        else if (game.in_draw()) statusText = 'Hòa cờ!';
        else if (game.in_check()) statusText += ' (ĐANG BỊ CHIẾU!)';

        statusEl.innerText = statusText;

        board.set({
            turnColor: game.turn() === 'w' ? 'white' : 'black',
            movable: {
                color: game.turn() === 'w' ? 'white' : 'black',
                dests: getValidMoves()
            }
        });
    }

    // 3. Khởi tạo bàn cờ (Chessground)
    const boardEl = document.getElementById('chess-board');
    const config = {
        fen: game.fen(),
        orientation: 'white',
        movable: {
            free: false,
            color: 'white',
            dests: getValidMoves()
        },
        events: {
            move: onMove
        }
    };

    // Cách khởi tạo linh hoạt tùy theo phiên bản CDN
    const cgFunc = (typeof Chessground === 'function') ? Chessground : Chessground.Chessground;
    board = cgFunc(boardEl, config);
    
    updateBoardStatus();
    console.log("Bàn cờ đã được khởi tạo THÀNH CÔNG!");

    // Nút reset
    document.getElementById('reset-btn').addEventListener('click', () => {
        game.reset();
        board.set({
            fen: game.fen(),
            movable: { color: 'white', dests: getValidMoves() }
        });
        updateBoardStatus();
    });
});
