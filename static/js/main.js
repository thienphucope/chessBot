$(function() {
    var board = null;
    var game = new Chess();
    var socket = io();
    var isRunning = false;
    var rolesLocked = false;
    var aiDelay = 0.5;

    socket.on('board_state', function(data) {
        game.load(data.fen);
        board.position(game.fen());
        updateStatus();
        updateMoveHistory(data.last_move_san, data.turn_count, data.move_annotation, data.move_time, data.total_time);
        updateEvalBar(data.evaluation);
        updateBoardAnnotations(data.move_annotation, data.last_move_uci);
        updateTotalTimeDisplay(data.white_total_time, data.black_total_time);
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

    socket.on('ai_settings_sync', function(data) {
        aiDelay = Number(data.thinking_delay || 0);
        $('#ai-delay-input').val(aiDelay.toFixed(1));
        $('#thinking-time').text(aiDelay.toFixed(1));
        setDelayMessage('Da cap nhat AI delay thanh ' + aiDelay.toFixed(1) + 's.', 'success');
    });

    socket.on('ai_settings_error', function(data) {
        setDelayMessage(data.message || 'Khong the cap nhat AI delay.', 'error');
    });

    function updateUI() {
        $('#white-role, #black-role').prop('disabled', rolesLocked);
        if (isRunning) { $('#start-btn').hide(); $('#pause-btn').show(); }
        else { $('#start-btn').show(); $('#pause-btn').hide(); }
    }

    function setDelayMessage(message, type) {
        var el = $('#ai-delay-message');
        el.text(message);
        el.removeClass('error success');
        if (type) el.addClass(type);
    }

    function updateStatus() {
        var turn = game.turn() === 'w' ? 'Trắng' : 'Đen';
        var statusText = 'Lượt đi: ' + turn;
        if (game.in_checkmate()) statusText = 'Chiếu bí! ' + turn + ' thua.';
        else if (game.in_draw()) statusText = 'Hòa cờ!';
        else if (game.in_check()) statusText += ' (CHIẾU!)';
        $('#status').text(statusText);
    }

    function updateMoveHistory(san, count, annotation, moveTime, totalTime) {
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

        var timeHtml = moveTime ? ` <span class="move-time">(${moveTime.toFixed(4)}s)</span>` : '';

        var movesList = $('#moves-list');
        if (count % 2 !== 0) { // White
            var moveNum = Math.floor(count / 2) + 1;
            var row = $('<div class="move-row" id="move-row-' + moveNum + '"></div>');
            row.append(`<span class="move-num">${moveNum}.</span>`);
            row.append(`<span class="move-val">${san}${annotationHtml}${timeHtml}</span>`);
            movesList.append(row);
        } else { // Black
            var moveNum = Math.floor(count / 2);
            $('#move-row-' + moveNum).append(`<span class="move-val">${san}${annotationHtml}${timeHtml}</span>`);
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

    function updateBoardAnnotations(annotation, lastMoveUci) {
        // Clear previous annotations
        $('.square-annotation').remove();

        if (!annotation || !lastMoveUci) return;

        // Get the target square of the last move
        var targetSquare = lastMoveUci.slice(-2);

        // Create annotation element
        var annotationEl = $('<div class="square-annotation"></div>');
        annotationEl.text(annotation);

        // Add appropriate class for styling
        if (annotation === '!!') annotationEl.addClass('brilliant-move');
        else if (annotation === '!') annotationEl.addClass('great-move');
        else if (annotation === 'Best') annotationEl.addClass('best-move');
        else if (annotation === 'Excellent') annotationEl.addClass('excellent-move');
        else if (annotation === 'Good') annotationEl.addClass('good-move');
        else if (annotation === '?!') annotationEl.addClass('inaccuracy-move');
        else if (annotation === '?') annotationEl.addClass('mistake-move');
        else if (annotation === '??') annotationEl.addClass('blunder-move');

        // Position the annotation on the target square
        var squareEl = $('#board .square-' + targetSquare);
        if (squareEl.length > 0) {
            squareEl.append(annotationEl);
        }
    }

    function updateTotalTimeDisplay(whiteTime, blackTime) {
        // Update total time in the controls panel
        whiteTime = whiteTime || 0;
        blackTime = blackTime || 0;

        // Add total time display to the controls if it doesn't exist
        if ($('#total-time-white').length === 0) {
            $('.bot-stats').append('<p id="total-time-display">Tổng thời gian: <span id="total-time-white">0.0s</span> / <span id="total-time-black">0.0s</span></p>');
        }

        $('#total-time-white').text(whiteTime.toFixed(4) + 's');
        $('#total-time-black').text(blackTime.toFixed(4) + 's');
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
        // Check if this is a pawn promotion
        var piece = game.get(source);
        if (piece && piece.type === 'p' && ((piece.color === 'w' && target[1] === '8') || (piece.color === 'b' && target[1] === '1'))) {
            // Show promotion dialog
            showPromotionDialog(source, target);
            return;
        }

        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';
        socket.emit('move', { 'move': source + target });
    }

    function showPromotionDialog(source, target) {
        var color = game.get(source).color;
        var pieces = color === 'w' ? ['q', 'r', 'b', 'n'] : ['q', 'r', 'b', 'n'];

        // Create dialog
        var dialog = $('<div id="promotion-dialog" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 1px solid black; z-index: 1000;"></div>');
        dialog.append('<h3>Chọn quân phong cấp:</h3>');

        pieces.forEach(function(piece) {
            var pieceName = piece === 'q' ? 'Hậu' : piece === 'r' ? 'Xe' : piece === 'b' ? 'Tượng' : 'Mã';
            var img = $('<img src="/static/img/chesspieces/wikipedia/' + (color === 'w' ? 'w' : 'b') + piece.toUpperCase() + '.png" style="width: 50px; height: 50px; margin: 5px; cursor: pointer;" title="' + pieceName + '">');
            img.on('click', function() {
                var move = game.move({ from: source, to: target, promotion: piece });
                if (move === null) {
                    alert('Nước đi không hợp lệ!');
                    return 'snapback';
                }
                socket.emit('move', { 'move': source + target + piece });
                dialog.remove();
            });
            dialog.append(img);
        });

        $('body').append(dialog);
    }

    $('#start-btn').on('click', function() {
        isRunning = true;
        rolesLocked = true;
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
        $('#total-time-display').remove();
        $('#eval-bar-fill').css('height', '50%');
        $('#eval-text').text('0.0');
        isRunning = false;
        rolesLocked = false;
        updateUI();
    });

    $('#white-role, #black-role').on('change', function() {
        socket.emit('set_roles', { white: $('#white-role').val(), black: $('#black-role').val() });
    });

    $('#apply-delay-btn').on('click', function() {
        var value = Number($('#ai-delay-input').val());
        if (!Number.isFinite(value) || value < 0 || value > 10) {
            setDelayMessage('AI delay phai nam trong khoang 0-10 giay.', 'error');
            return;
        }
        socket.emit('set_ai_delay', { delay: value });
    });

    $('#ai-delay-input').on('keydown', function(event) {
        if (event.key === 'Enter') {
            $('#apply-delay-btn').trigger('click');
        }
    });

    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        castle: true,
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: function() { board.position(game.fen()); }
    });
    updateStatus();
    $('#thinking-time').text(aiDelay.toFixed(1));
});
