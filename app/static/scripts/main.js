(function() {
    var Message, url;
    Message = function(arg) {
        (this.text = arg.text), (this.message_side = arg.message_side);
        this.draw = (function(_this) {
            return function() {
                var $message;
                $message = $(
                    $('.message_template')
                        .clone()
                        .html()
                );
                $message
                    .addClass(_this.message_side)
                    .find('.text')
                    .html(_this.text);
                if (this.message_side === 'left') {
                    url = '/static/images/bot.png';
                } else {
                    url = '/static/images/user.png';
                }
                $message
                    .find('.avatar')
                    .css('background-image', 'url(' + url + ')');
                $('.messages').append($message);
                return setTimeout(function() {
                    return $message.addClass('appeared');
                }, 0);
            };
        })(this);
        return this;
    };
    $(function() {
        var getMessageText, sendMessage;
        var socket = io.connect("http://localhost:80/kafka")
        socket.on("kafkaconsumer",(msg) => receiveMessage(msg));


        getMessageText = function() {
            var $message_input;
            $message_input = $('.message_input');
            return $message_input.val();
        };

        receiveMessage = function(text) {
            var $messages, message, messages_list, msg_idx;
            $messages = $('.messages');
            message = new Message({
                    text: text,
                    message_side: 'left'
                });
            message.draw();
            
            return $messages.stop().animate(
                { scrollTop: $messages.prop('scrollHeight') },
               700
            );
        };

        sendMessage = function(text) {
            var $messages, message, messages_list, msg_idx;
            if (text.trim() === '') {
                return;
            }
            $('.message_input').val('');
            $messages = $('.messages');
            message = new Message({
                text: text,
                message_side: 'right'
            });
            message.draw();
         
            socket.emit("kafkaproducer", text)
         
            return $messages.stop().animate(
                { scrollTop: $messages.prop('scrollHeight') },
               700
            );
        };
        
        $('.send_message').click(function() {
            return sendMessage(getMessageText());
        });
        $('.message_input').keyup(function(e) {
            if (e.which === 13) {
                return sendMessage(getMessageText());
            }
        });
        var message_greetings = new Message({
            text: 'Hi, I am DialoGPT. How can I help you?',
            message_side: 'left'
        });
        message_greetings.draw();
    });
}.call(this));
