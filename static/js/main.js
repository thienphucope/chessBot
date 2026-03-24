/**
 * main.js - Quản lý giao diện và kết nối Socket.io
 */

$(function() {
    var board = null;
    var game = new Chess();
    var socket = io();
    var isRunning = false;

    // --- SOCKET HANDLERS ---
    socket.on('board_state', function(data) {
        game.load(data.fen);
        board.position(game.fen());
        updateStatus();
        updateMoveHistory(data.last_move_san, data.turn_count, data.move_annotation);
        updateEvalBar(data.evaluation);
    });

    socket.on('game_over', function(data) {
        isRunning = false;
        updateUI();
        alert('Ván cờ kết thúc! Kết quả: ' + data.result);
    });

    socket.on('game_state_sync', function(data) {
        isRunning = data.is_running;
        updateUI();
    });

    // --- FUNCTIONS ---
    function updateUI() {
        if (isRunning) {
            $('#start-btn').hide();
            $('#pause-btn').show();
        } else {
            $('#start-btn').show();
            $('#pause-btn').hide();
        }
    }

    function updateStatus() {
        var turn = game.turn() === 'w' ? 'Trắng' : 'Đen';
        var statusText = 'Lượt đi: ' + turn;
        
        if (game.in_checkmate()) statusText = 'Chiếu bí! ' + turn + ' thua.';
        else if (game.in_draw()) statusText = 'Hòa cờ!';
        else if (game.in_check()) statusText += ' (CHIẾU!)';
        
        $('#status').text(statusText);
    }

    function updateMoveHistory(san, count, annotation) {
        if (!san) return;

        var annotationHtml = '';
        if (annotation) {
            let colorClass = '';
            if (annotation === '!!' || annotation === '!') colorClass = 'good-move';
            if (annotation === '?!' || annotation === '?') colorClass = 'inaccuracy-move';
            if (annotation === '??') colorClass = 'blunder-move';
            annotationHtml = ` <span class="move-annotation ${colorClass}">${annotation}</span>`;
        }

        var movesList = $('#moves-list');
        if (count % 2 !== 0) { // Lượt của Trắng
            var moveNum = Math.floor(count / 2) + 1;
            var row = $('<div class="move-row" id="move-row-' + moveNum + '"></div>');
            row.append(`<span class="move-num">${moveNum}.</span>`);
            row.append(`<span class="move-val">${san}${annotationHtml}</span>`);
            movesList.append(row);
        } else { // Lượt của Đen
            var moveNum = Math.floor(count / 2);
            $('#move-row-' + moveNum).append(`<span class="move-val">${san}${annotationHtml}</span>`);
        }
        // Tự động cuộn xuống cuối
        movesList.scrollTop(movesList[0].scrollHeight);
    }

    function updateEvalBar(score) {
        if (score === undefined) return;
        
        // Hiển thị text
        var displayScore = score > 0 ? '+' + score.toFixed(1) : score.toFixed(1);
        $('#eval-text').text(displayScore);

        // Tính toán chiều cao (score từ -10 đến 10)
        // % = 50 + (score * 5)
        var percentage = 50 + (score * 5);
        percentage = Math.max(5, Math.min(95, percentage));
        
        $('#eval-bar-fill').css('height', percentage + '%');
    }

    function onDragStart(source, piece, position, orientation) {
        if (game.game_over() || !isRunning) return false;

        var turn = game.turn();
        var whiteRole = $('#white-role').val();
        var blackRole = $('#black-role').val();

        // Chặn nếu không phải lượt của người
        if (turn === 'w' && whiteRole !== 'human') return false;
        if (turn === 'b' && blackRole !== 'human') return false;

        // Chặn nếu kéo quân sai màu
        if ((turn === 'w' && piece.search(/^b/) !== -1) ||
            (turn === 'b' && piece.search(/^w/) !== -1)) {
            return false;
        }
    }

    function onDrop(source, target) {
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';
        
        socket.emit('move', { 'move': source + target });
    }

    // --- EVENTS ---
    $('#start-btn').on('click', function() {
        isRunning = true;
        socket.emit('toggle_game', { running: true });
        updateUI();
    });

    $('#pause-btn').on('click', function() {
        isRunning = false;
        socket.emit('toggle_game', { running: False }); // Backend cần lowercase false
        socket.emit('toggle_game', { running: false });
        updateUI();
    });

    $('#reset-btn').on('click', function() {
        socket.emit('reset');
        $('#moves-list').empty();
        $('#eval-bar-fill').css('height', '50%');
        $('#eval-text').text('0.0');
        isRunning = false;
        updateUI();
    });

    $('#white-role, #black-role').on('change', function() {
        socket.emit('set_roles', { 
            white: $('#white-role').val(), 
            black: $('#black-role').val() 
        });
    });

    // --- INIT ---
    var config = {
        draggable: true,
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: function() { board.position(game.fen()); }
    };
    board = Chessboard('board', config);
    updateStatus();
});
