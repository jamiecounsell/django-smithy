/**
 * Initialize CodeMirror. Also hide the body input
 * field when the METHOD is set to GET or when the body
 * type is set to application/x-www-form-urlencoded.
 */
(function ($) {

    function has_body(method) {
        return method === 'PUT' || method === 'POST';
    }

    var TYPE_URL = 'application/x-www-form-urlencoded';

    $(document).on("DOMContentLoaded", function(event) {
        var body_row = document.querySelector(".form-row.field-body");
        var method_row = document.querySelector(".form-row.field-content_type");

        var inline = document.getElementById("body_parameters-group");
        var code = document.getElementById("id_body");
        var method = document.getElementById("id_method");
        var type = document.getElementById("id_content_type");

        function toggle_content_type() {
            if (!has_body(method.value)) {
                method_row.style.display = 'none';
            } else {
                method_row.style.display = 'block';
            }
        }

        function toggle_body() {
            if (!has_body(method.value) || type.value === TYPE_URL) {
                body_row.style.display = 'none';
            } else {
                body_row.style.display = 'block';
            }
            toggle_content_type();
        }

        function toggle_body_inline() {
            var m = type.value;
            if (m === TYPE_URL) {
                inline.style.display = 'block';
            } else {
                inline.style.display = 'none';
            }
            toggle_body();
        }

        window.editor = CodeMirror.fromTextArea(code, {
            mode: 'django',
            lineNumbers: true
        });

        $(method).on('change', toggle_body);
        $(type).on('change', toggle_body_inline);
        toggle_body_inline();

    });
})(django.jQuery);


/**
 * Switch to password inputs when the field name
 * contains terms like "key" or "pass"
 */
(function ($) {
    function set_type(id, type) {
        $('#' + id).attr("type", type);
    }

    function check($el) {
        $el = $el.target ? $el.target : $el;
        var name = $el.value;
        var id = $el.id;
        var target_id = id.replace(/-name$/, '-value');
        if (/pass|key|secret|token/.test(name)) {
            set_type(target_id, 'password');
        } else {
            set_type(target_id, 'text');
        }
    }

    function sensitive_data_hiding() {
        document.querySelectorAll("#variables-group .field-name > input[type='text']").forEach(function (field) {
            check(field);
            field.removeEventListener('change', check);
            field.addEventListener('change', check);
        });
    }

    $(document).on("DOMContentLoaded", sensitive_data_hiding);
    $(document).on("formset:added", sensitive_data_hiding);
})(django.jQuery);
