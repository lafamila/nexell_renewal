/******************************************************************************
 * 메세지를 팝업한다.
 */
$.alert = function(title, options) {

    var alert_width = '330px';
    var alert_title = title;
    var alert_contents = '';
    var button_label = '확인';
    var button_action = function(event) { $('#yawn_alert').modal('hide'); };

    if (typeof(options) === 'function') {
        button_action = options;
    } else if (typeof(options) === 'object') {
        if (typeof(options.width) === 'string') {
            alert_width = options.width;
        }
        if (typeof(options.contents) === 'string') {
            alert_contents = options.contents;
        }
        if (typeof(options.button) === 'string') {
            button_label = options.button;
        } else if (typeof(options.button) === 'object') {
            if (typeof(options.button.label) === 'string') {
                button_label = options.button.label;
            }
            if (typeof(options.button.action) === 'function') {
                button_action = options.button.action;
            }
        }
    }

    var html = '';
    html += '<div class="modal fade" style="margin-top:150px;" data-backdrop="static" id="yawn_alert">';
    html += '    <div class="modal-dialog" style="width:'+alert_width+'">';
    html += '        <div class="modal-content">';
    html += '            <div class="modal-body text-center" style="margin:15px;">'; 
    html += '                <h4 class="confirm-message"><b>'+alert_title+'</b></h4>';
    html += alert_contents;
    html += '            </div>';
    html += '            <div class="modal-footer" style="padding-top:10px;border-top:0px;">';
    html += '                <div class="text-center" style="padding-bottom:15px;">';
    html += '                    <a class="btn btn-danger btn-sm" id="btnAlertOK">'+button_label+'</a>'; //홈페이지로 이동
    html += '                </div>';
    html += '            </div>';
    html += '        </div>';
    html += '    </div>';
    html += '</div>';

    if ($('body').find('#yawn_alert').length !== 0) {
        $('body').find('#yawn_alert').remove();
    }
    $('body').append(html);

    $('#btnAlertOK').on('click', function(event) {
        button_action(event);
    });

    $('#yawn_alert').modal('show');
};