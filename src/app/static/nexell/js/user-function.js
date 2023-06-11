/******************************************************************************
 * for mobile check
 */
function mobileCheck() {
    var check = false;
    (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
    return check;
};

/******************************************************************************
 * 오류를 팝업합니다.
 */
function alertError(xhr, status, error) {
    var msg = '';
    msg += '알수없는 오류가 발생하였습니다.';
    msg += '\n오류가 지속될 경우 관리자에게 연락하시기 바랍니다.';
    msg += '\n\n' + status + ':' + error;
    alert(msg);
    console.log(xhr.responseText);
}

/******************************************************************************
 * 오류를 팝업합니다.
 */
function fnAlert(pMessage, pType = 'success', pTimeout = 2000)
{
    var _color = 'rgb(115, 158, 115)';
    var _timeout = pTimeout;
    if (pType == 'error') {
        _color = '#f00';
        _timeout = 5000;
    }

    $.smallBox({
        // title : pTitle, //'<i class="fa fa-clock-o"></i> '+ pMessage,
        content : '<div class="padding-top:4px;"><i class="fa fa-check"></i> ' + pMessage + '</div>',
        color : _color,
        timeout : _timeout,
        // icon : "fa fa-bell"
        // iconSmall : "fa fa-thumbs-up",
    });
}

/******************************************************************************
 * 오류를 팝업합니다.
 */
function fnGetMessage(pMessage)
{
    if (!pMessage.indexOf('Warning')) {
        if (pMessage.indexOf('POST Content-Length')) {
            return '컨텐츠 전송 용량을 초과하였습니다.'; // POST Content-Length of 
        }
    }
    return pMessage.replaceAll('<br />','');
}

/******************************************************************************
 * 오류를 팝업합니다.
 */
function toastrError(pJqXHR) {
    var message = '';
    message += '알 수 없는 오류가 발생하였습니다.';
    message += '\n';
    message += '오류가 지속될 경우 관리자에게 연락하시기 바랍니다.';
    message += `\nMessage : ${pJqXHR.responseText}`;
    toastrMessage('error', message);
    console.error('error', pJqXHR);
}

/******************************************************************************
 * 오류를 팝업합니다.
 * 
 * [positionClass]
 *  toast-top-center
 *  toast-bottom-full-width
 *  toast-top-full-width
 */
function toastrMessage(type, message, title = '')
{
    if (typeof(message) !== 'string')
    {
        if (message.status === 401)
        {
            location.href = '/';
            return false;
        }
        var tmp = message.responseText;
        if (tmp === '')
        {
            tmp = message.status + ' ' + message.statusText;
        }
        message = tmp;
    }
    
    if (toastr !== null)
    {
        toastr.options.positionClass = 'toast-top-full-width';
        if (type === 'success'){
            toastr.options.positionClass = 'toast-bottom-right';
            toastr.options.timeOut = 2000;
        } else if (type === 'info') {
            toastr.options.timeOut = 2000;
        } else if (type === 'warning') {
            toastr.options.timeOut = 2000;
        } else if (type === 'debug') {
            toastr.options.timeOut = 0;
        } else if (type === 'error') {
            toastr.options.timeOut = 0;
            if (message.indexOf('<body>') > 0) {
                var tmp = $(message);
                for (var i=0; i<tmp.length; i++) {
                    if ($(tmp[i]).context.id === 'container') {
                        message = $(tmp[i]).context.innerHTML;
                        message = message.replace('<h1', '<h3 style="margin:0px;"');
                    }
                }
            }
            if (title === '') {
                title = '<p></p>';
            }
        } else {
            console.error('toastrMessage', '"'+type+'" is an undefined value.');
        }
    }

    if (toastr !== null)
    {
        toastr[type](message, title);
    }
    else
    {
        alert(message);
    }
}

/******************************************************************************
 * 기능명    : 값이 비어있는지 확인합니다.
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 * 
 * @param   {string}    pValue - 비교값
 */
function fnIsEmpty(pValue) {
    if (pValue == null || pValue == '') {
        return true;
    }
    return false;
}

/******************************************************************************
 * 기능명    : 
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 * 
 * @param   {string}    pMode - 로더 페이지 상태
 */
var loadding = false;
var loaddingPage = [];
function fnLoadding(pMode = 'show')
{
    // console.log('fnLoadding', pMode);
    if (pMode == 'hide') {
        loaddingPage.shift();
        if (loaddingPage.length == 0) {
            $('.yawnLoader').hide();
        }
    } else {
        loaddingPage.push(location.href);
        if (loadding) {
            $('.yawnLoader').show();
        } else {
            $('.yawnLoader').fakeLoader({
                repeat: true,
                bgColor: 'rgba(255, 255, 255, 0.2)',
                spinner: 'spinner2'
            });
            loadding = true;
        }
    }
}

/******************************************************************************
 * 기능명    : 
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 */
function setCookie(cookieName, value, exdays){
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var cookieValue = escape(value) + ((exdays==null) ? "" : "; expires=" + exdate.toGMTString());
    document.cookie = cookieName + "=" + cookieValue;
}
 
/******************************************************************************
 * 기능명    : 
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 */
function deleteCookie(cookieName){
    var expireDate = new Date();
    expireDate.setDate(expireDate.getDate() - 1);
    document.cookie = cookieName + "= " + "; expires=" + expireDate.toGMTString();
}
 
/******************************************************************************
 * 기능명    : 
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 */
function getCookie(cookieName) {
    cookieName = cookieName + '=';
    var cookieData = document.cookie;
    var start = cookieData.indexOf(cookieName);
    var cookieValue = '';
    if(start != -1){
        start += cookieName.length;
        var end = cookieData.indexOf(';', start);
        if(end == -1)end = cookieData.length;
        cookieValue = cookieData.substring(start, end);
    }
    return unescape(cookieValue);
}

/******************************************************************************
 * 기능명    : HTML문서를 Excel로 Export합니다.
 * 작성자    : 마프 정준교
 * 작성일자  : 2018-01-18
 * 
 * @param   {string}    pFilename 출력파일명
 * @param   {string}    pATagID 링크 앵커아이디
 * @param   {string}    pContentsID 출력할 컨텐츠아이디
 * @param   {string}    pSheetName 시트명(미입력시 기본시트명으로 지정)
 */
function fnExportExcel(pFilename, pATagID, pContentsID, pSheetName = 'Sheet1')
{
    var exportHtml = '<html xmlns:v="urn:schemas-microsoft-com:vml" ';
       exportHtml += '      xmlns:o="urn:schemas-microsoft-com:office:office" ';
       exportHtml += '      xmlns:x="urn:schemas-microsoft-com:office:excel"> ';
       exportHtml += '    <head>\n';
       exportHtml += '        <xml>\n';
       exportHtml += '            <x:ExcelWorkbook>\n';
       exportHtml += '                <x:ExcelWorksheets>\n';
       exportHtml += '                    <x:ExcelWorksheet>\n';
       exportHtml += '                        <x:Name>'+pSheetName+'</x:Name>\n';
       exportHtml += '                        <x:WorksheetOptions>\n';
       exportHtml += '                            <x:Panes></x:Panes>\n';
       exportHtml += '                        </x:WorksheetOptions>\n';
       exportHtml += '                    </x:ExcelWorksheet>\n';
       exportHtml += '                </x:ExcelWorksheets>\n';
       exportHtml += '            </x:ExcelWorkBook>\n';
       exportHtml += '        </xml>\n';
       exportHtml += '        <style>\n';
       exportHtml += '            th, td { border: .5pt solid #000; }\n';
       exportHtml += '            th { background: #eee; }\n';
       exportHtml += '        </style>\n';
       exportHtml += '    </head>\n';
       exportHtml += '    <body>\n';
       exportHtml += '\n';
       exportHtml +=          $(pContentsID).html();
       exportHtml += '\n';
       exportHtml += '    </body>\n';
       exportHtml += '</html>\n';

    var dataType = 'data:application/vnd.ms-excel';

    alert(exportHtml);

    $(pATagID).attr('href', dataType + ', ' + encodeURIComponent(exportHtml));
    $(pATagID).attr('_download', pFilename);
}

/******************************************************************************
 * 지정된 패턴으로 오늘 일시를 반환합니다.
 * 
 * @param {string} pPattern 
 * @param {string} pOption 
 * @param {string} pApplyDate 
 */
function fnToday(pPattern = 'ymd', pOption = '', pApplyDate = '')
{
    var result = pPattern.toUpperCase();
    var today = pApplyDate == '' ? new Date() : new Date(pApplyDate);
    if (pOption != '') {
        var type = pOption.substring(pOption.length, pOption.length-1).toUpperCase();
        var period = parseInt(pOption.substring(0, pOption.length-1).trim());
        // console.log(type, period);
        if (type == 'Y') {
            today.setFullYear(today.getFullYear() + period);
        } else if (type == 'M') {
            today.setMonth(today.getMonth() + period);
        } else if (type == 'D') {
            today.setDate(today.getDate() + period);
        } else if (type == 'H') {
            today.setHours(today.getHours() + period);
        } else if (type == 'I') {
            today.setMinutes(today.getMinutes() + period);
        } else if (type == 'S') {
            today.setSeconds(today.getSeconds() + period);
        }
    }

    var year = today.getFullYear();
    var month = today.getMonth()+1;
        month = month < 10 ? '0'+month : month;
    var day = today.getDate();
        day = day < 10 ? '0'+day : day;
    var hour = today.getHours();
        hour = hour < 10 ? '0'+hour : hour;
    var minute = today.getMinutes();
        minute = minute < 10 ? '0'+minute : minute;
    var second = today.getSeconds();
        second = second < 10 ? '0'+second : second;

    result = result.replaceAll('Y', year);
    result = result.replaceAll('M', month);
    result = result.replaceAll('D', day);
    result = result.replaceAll('H', hour);
    result = result.replaceAll('I', minute);
    result = result.replaceAll('S', second);

    return result;
}

/******************************************************************************
 * 
 */
function fnDateAdd(pValue)
{
    var result = '';
    var valArrs = pValue.split(' ');
    var tmpDate = valArrs[0].split('-');
    var tmpDays = parseInt(valArrs[1]);
    var tmpType = valArrs[2];
    console.log(tmpDate, tmpDays, tmpType);
    if (tmpType == 'year') {
        var tmp = new Date(tmpDate[0], tmpDate[1], tmpDate[2]+(365*tmpDays));
        var year = tmp.getFullYear();
        var month = tmp.getMonth() < 10 ? '0'+tmp.getMonth() : tmp.getMonth();
        var day = tmp.getDate() < 10 ? '0'+tmp.getDate() : tmp.getDate();
        result = year+'-'+month+'-'+day;
    } else {
        var tmp = new Date(tmpDate[0], tmpDate[1], tmpDate[2]+(tmpDays));
        var year = tmp.getFullYear();
        var month = tmp.getMonth() < 10 ? '0'+tmp.getMonth() : tmp.getMonth();
        var day = tmp.getDate() < 10 ? '0'+tmp.getDate() : tmp.getDate();
        result = year+'-'+month+'-'+day;
    }
    return result;
}

function fnGetFirstDay(pValue)
{
    var tmpDate = new Date(pValue);
    var tmpDate = new Date(tmpDate.getFullYear(), tmpDate.getMonth(), 1);
    var year = tmpDate.getFullYear();
    var month = tmpDate.getMonth()+1; month = month < 10 ? '0'+ month : month;
    var day = tmpDate.getDate(); day = day < 10 ? '0'+ day : day;
    console.log(year+'-'+month+'-'+day);
    return year+'-'+month+'-'+day;
}

function fnGetLastDay(pValue)
{
    var tmpDate = new Date(pValue);
    var tmpDate = new Date(tmpDate.getFullYear(), tmpDate.getMonth()+1, 0);
    var year = tmpDate.getFullYear();
    var month = tmpDate.getMonth()+1; month = month < 10 ? '0'+ month : month;
    var day = tmpDate.getDate(); day = day < 10 ? '0'+ day : day;
    console.log(year+'-'+month+'-'+day);
    return year+'-'+month+'-'+day;
}