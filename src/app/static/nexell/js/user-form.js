/******************************************************************************ㄴ
 * 폼 데이터를 반환합니다.
 */
function getFormData(form) {

    var formData = new FormData(form);

    /*
    for (var i=0; i<$('.basic_item7').length; i++) {
        $.each($('.basic_item7')[i].files, function(i, file) {
            formData.append(i, file);
        });
    }
    */

    // var tmp = $(form).find('input');
    // for (var i=0; i<tmp.length; i++) {
    //     var obj = $(tmp[i]);
    //     if (obj.attr('type') == 'hidden' || obj.attr('type') == 'text' || obj.attr('type') == 'password' || obj.attr('type') == 'tel' || obj.attr('type') == 'number') {
    //         if (obj.val().trim() != '') {
    //             console.log(obj.attr('name'), obj.val());
    //             // formData.append(obj.attr('name'), obj.val());
    //         }
    //     } else if (obj.attr('type') == 'radio' || obj.attr('type') == 'checkbox') {
    //         if (obj.is(':checked')) {
    //             console.log(obj.attr('name'), obj.val());
    //             // formData.append(obj.attr('name'), obj.val());
    //         }
    //     }
    // }

    // var tmp = $(form).find('textarea');
    // for (var i=0; i<tmp.length; i++) {
    //     var obj = $(tmp[i]);
    //     if (obj.val().trim() != '') {
    //         console.log(obj.attr('name'), obj.val());
    //         // formData.append(obj.attr('name'), obj.val());
    //     }
    // }

    // var tmp = $(form).find('select');
    // for (var i=0; i<tmp.length; i++) {
    //     var obj = $(tmp[i]);
    //     console.log(obj.attr('name'), obj.val());
    //     // formData.append(obj.attr('name'), obj.val());
    // }

    return formData;
}

/******************************************************************************ㄴ
 * 폼 데이터를 반환합니다.
 */
function initForm(modal) {
    modal.find('.modal-title').html('(title)');
    modal.find('form')[0].reset();
    modal.find('select option:selected').attr('selected', false);
    modal.find('.has-error').removeClass('has-error');
    modal.find('.alert-block').remove();
}

/******************************************************************************
 * 폼 체크 함수 정의
 */
function _v_showMessage(id, message) {
    try {
        if ($('#'+id).length === 0) {
            throw 'The element("'+id+'") can not be found.';
        }

        var help = $('#'+id).parent().find('.alert-block');
        if (help.length === 0) {
            $('#'+id).parent().append('<span class="alert-block error"></span>');
        }

        $('#'+id).parent().addClass('has-error');
        $('#'+id).parent().find('.alert-block').html(message);
        $('#'+id).parent().find('.alert-block').removeClass('hide');
    } catch(e) {
        console.error('_v_showMessage', e);
    }
}

function _v_hideMessage(id) {
    try {
        if ($('#'+id).length === 0) {
            throw 'The element("'+id+'") can not be found.';
        }

        $('#'+id).parent().removeClass('has-error');
        $('#'+id).parent().find('.alert-block').html('');
        $('#'+id).parent().find('.alert-block').addClass('hide');
    } catch(e) {
        console.error('_v_hideMessage', e);
    }
}

function _v_isNotEmpty(id) {
    try {
        if ($('#'+id).length === 0) {
            throw 'The element("'+id+'") can not be found.';
        }

        var val = $('#'+id).val();
        if ($('#'+id).data('mask') !== undefined) {
            var mask = $('#'+id).data('mask').replaceAll('9','_');
            if (val === mask) {
                val = '';
            }
        }

        if (val === '') {
            _v_showMessage(id, '필수 정보입니다.')
            return false;
        } else {
            _v_hideMessage(id);
            return true;
        }
    } catch(e) {
        console.error('_v_emptyCheck', e);
    }
}

var validate = [];
function _v_emptyCheck(list) {

    validate = [];

    if (typeof(list) !== 'object') {
        console.error('_v_emptyCheck', 'Variable types do not match.');
        return false;
    }

    for (var i=0; i<list.length; i++) {
        validate.push(_v_isNotEmpty(list[i]));
    }

    for (var i=0; i<validate.length; i++) {
        if (validate[i] === false) {
            return false;
        }
    }

    return true;
}
