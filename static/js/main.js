$(function() {
    var board = null;
    var game = new Chess();
    var socket = io();
    var isRunning = false;

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
        // Chờ 500ms để animation của bàn cờ kịp hoàn tất nước đi cuối
        setTimeout(function() {
            alert('Ván cờ kết thúc! Kết quả: ' + data.result);
        }, 500);
    });

    socket.on('game_state_sync', function(data) {
        isRunning = data.is_running;
        updateUI();
    });

    function updateUI() {
        if (isRunning) { $('#start-btn').hide(); $('#pause-btn').show(); }
        else { $('#start-btn').show(); $('#pause-btn').hide(); }
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
            let label = annotation;
            
            // Map label to Chess.com classes
            if (annotation === '!!') colorClass = 'brilliant-move';
            else if (annotation === '!') colorClass = 'great-move';
            else if (annotation === 'Best') colorClass = 'best-move';
            else if (annotation === 'Excellent') colorClass = 'excellent-move';
            else if (annotation === 'Good') colorClass = 'good-move';
            else if (annotation === '?!') colorClass = 'inaccuracy-move';
            else if (annotation === '?') colorClass = 'mistake-move';
            else if (annotation === '??') colorClass = 'blunder-move';

            annotationHtml = ` <span class="move-annotation ${colorClass}">${label}</span>`;
        }

        var movesList = $('#moves-list');
        if (count % 2 !== 0) { // White
            var moveNum = Math.floor(count / 2) + 1;
            var row = $('<div class="move-row" id="move-row-' + moveNum + '"></div>');
            row.append(`<span class="move-num">${moveNum}.</span>`);
            row.append(`<span class="move-val">${san}${annotationHtml}</span>`);
            movesList.append(row);
        } else { // Black
            var moveNum = Math.floor(count / 2);
            $('#move-row-' + moveNum).append(`<span class="move-val">${san}${annotationHtml}</span>`);
        }
        movesList.scrollTop(movesList[0].scrollHeight);
    }

    function updateEvalBar(score) {
        if (score === undefined) return;
        var displayScore = score > 0 ? '+' + score.toFixed(1) : score.toFixed(1);
        $('#eval-text').text(displayScore);
        var percentage = 50 + (score * 5);
        percentage = Math.max(5, Math.min(95, percentage));
        $('#eval-bar-fill').css('height', percentage + '%');
    }

    function onDragStart(source, piece, position, orientation) {
        if (game.game_over() || !isRunning) return false;
        var turn = game.turn();
        if ((turn === 'w' && $('#white-role').val() !== 'human') ||
            (turn === 'b' && $('#black-role').val() !== 'human')) return false;
        if ((turn === 'w' && piece.search(/^b/) !== -1) ||
            (turn === 'b' && piece.search(/^w/) !== -1)) return false;
    }

    function onDrop(source, target) {
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';
        socket.emit('move', { 'move': source + target });
    }

    $('#start-btn').on('click', function() {
        isRunning = true;
        socket.emit('toggle_game', { running: true });
        updateUI();
    });

    $('#pause-btn').on('click', function() {
        isRunning = false;
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
        socket.emit('set_roles', { white: $('#white-role').val(), black: $('#black-role').val() });
    });

    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: function() { board.position(game.fen()); }
    });
    updateStatus();
});
