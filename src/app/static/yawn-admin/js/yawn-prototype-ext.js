// only run when the substr() function is broken
if ('ab'.substr(-1) != 'b') {
    /**
     *  Get the substring of a string
     *  @param  {integer}  start   where to start the substring
     *  @param  {integer}  length  how many characters to return
     *  @return {string}
     */
    String.prototype.substr = function(substr) {
      return function(start, length) {
        // call the original method
        return substr.call(this,
          // did we get a negative start, calculate how much it is from the beginning of the string
          // adjust the start parameter for negative value
          start < 0 ? this.length + start : start,
          length)
      }
    }(String.prototype.substr);
}

/******************************************************************************
 * 폼 체크 함수 정의
 */
String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
}

/******************************************************************************
 * 폼 체크 함수 정의
 */
Array.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.join(',').replaceAll(search, replacement).split(',');
}

/******************************************************************************
 * 기능명    : 지정된 형식으로 포맷팅한 문자열을 반환한다.
 * 작성자    : 하이라인닷넷 정준교
 * 작성일자  : 2018-01-18
 * 
 * @param   {string}    pDataType 원본데이터유형
 * @param   {string}    pFormatType 포맷팅유형
 * @param   {string}    pDelimiter 구분자
 */
String.prototype.toFormat = function(pDataType, pFormatType, pDelimiter)
{
    var result = this;
    var dataType = pDataType.toUpperCase();
    var formatType = dataType;
    if (pFormatType !== undefined) {
        formatType = pFormatType.toUpperCase();
    }
    if (dataType === 'DATE') {
        if (pDelimiter === undefined) {
            pDelimiter = '/';
        }
        if (formatType === 'DATE') {
            if (result.length === 6) {
                result = result.substr(0,4) + pDelimiter
                    + result.substr(4,2);
            } else if (result.length === 8) {
                result = result.substr(0,4) + pDelimiter
                    + result.substr(4,2) + pDelimiter
                    + result.substr(6,2);
            } else if (result.length > 8) {
                result = result.substr(0,10);
            }
        }
    } else if (dataType === 'TIME') {
        if (pDelimiter === undefined) {
            pDelimiter = ':';
        }
        if (formatType === 'TIME') {
            if (result.length === 4) {
                result = result.substr(0,2) + pDelimiter
                    + result.substr(2,2);
            } else if (result.length === 6) {
                result = result.substr(0,2) + pDelimiter
                    + result.substr(2,2) + pDelimiter
                    + result.substr(4,2);
            }
        }
    } else if (dataType === 'DATETIME') {
        pDelimiter1 = '/';
        pDelimiter2 = ':';
        if (result.length === 12) {
            result = result.substr(0,4) + pDelimiter1
                + result.substr(4,2) + pDelimiter1
                + result.substr(6,2) + ' '
                + result.substr(8,2) + pDelimiter2
                + result.substr(10,2);
        } else if (result.length === 14) {
            result = result.substr(0,4) + pDelimiter1
                + result.substr(4,2) + pDelimiter1
                + result.substr(6,2) + ' '
                + result.substr(8,2) + pDelimiter2
                + result.substr(10,2) + pDelimiter2
                + result.substr(12,2);
        }
    } else if (dataType === 'NUMBER') {
        if (result != '') {
            result = result.replaceAll(',','');
            result = parseInt(result);
            result = result.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    } else if (dataType === 'SECOND') {
        if (pDelimiter === undefined) {
            pDelimiter = ':';
        }
        if (result == 'NaN') {
            result = '0';
        }
        var h = '';
        var m = '';
        var s = '';
        var second = parseInt(result);
        if (formatType === 'MINUTE') {
            m = parseInt((second/60)%60).toString();
            m = '0'.repeat(2-m.length) + m;
            s = parseInt(second%60).toString();
            s = '0'.repeat(2-s.length) + s;
            result = m + pDelimiter + s;
        } else if (formatType === 'TIME') {
            h = parseInt(second/(60*60)).toString();
            h = '0'.repeat(2-h.length) + h;
            m = parseInt((second/60)%60).toString();
            m = '0'.repeat(2-m.length) + m;
            s = parseInt(second%60).toString();
            s = '0'.repeat(2-s.length) + s;
            result = h + pDelimiter + m + pDelimiter + s;
        } else if (formatType === 'HOUR') {
            h = parseInt(second/(60*60)).toString();
            h = '0'.repeat(3-h.length) + h;
            m = parseInt((second/60)%60).toString();
            m = '0'.repeat(2-m.length) + m;
            s = parseInt(second%60).toString();
            s = '0'.repeat(2-s.length) + s;
            result = h + pDelimiter + m + pDelimiter + s;
        }
    }
    return result;
}

/******************************************************************************
 * 
 */
// Date.prototype.format = function(f) {
//     if (!this.valueOf()) return " ";
 
//     var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
//     var d = this;
     
//     return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
//         switch ($1) {
//             case "yyyy": return d.getFullYear();
//             case "yy": return (d.getFullYear() % 1000).zf(2);
//             case "MM": return (d.getMonth() + 1).zf(2);
//             case "dd": return d.getDate().zf(2);
//             case "E": return weekName[d.getDay()];
//             case "HH": return d.getHours().zf(2);
//             case "hh": return ((h = d.getHours() % 12) ? h : 12).zf(2);
//             case "mm": return d.getMinutes().zf(2);
//             case "ss": return d.getSeconds().zf(2);
//             case "a/p": return d.getHours() < 12 ? "오전" : "오후";
//             default: return $1;
//         }
//     });
// };

// String.prototype.string = function(len){var s = '', i = 0; while (i++ < len) { s += this; } return s;};
// String.prototype.zf = function(len){return "0".string(len - this.length) + this;};
// Number.prototype.zf = function(len){return this.toString().zf(len);};

/******************************************************************************
 * 
 */
Date.prototype.lastDay = function()
{
    // var target = this;
    var year = this.getFullYear();
    var month = (this.getMonth()+1); month = month < 10 ? '0'+ month : month;
    return new Date(year, month, 0);
}