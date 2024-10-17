document.addEventListener('DOMContentLoaded', function () {
    const section1 = document.getElementById('name-section');
    const section2 = document.getElementById('list-section');
    const section3 = document.getElementById('predict-section');
    const section4 = document.getElementById('df-section');
    const section5 = document.getElementById('wait-section');

    const sections = [section1, section2, section3, section4, section5];

    const csrf = document.getElementById('csrf').value
    function hideAllSection(toOpen){
        sections.forEach(function (el) {
            el.style.display = 'none';
        });
        toOpen.style.display = 'block';
    }

    function showError(section, text){
        let errorObj = section.querySelector('.error');
        errorObj.style.display = 'block';
        errorObj.innerText = text;
    }

    section1.querySelector('.next').addEventListener('click', function () {
        let name = document.getElementById('name').value;
        console.log(name);

        fetch('/constructor/start/check/name/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf
            },
            body: JSON.stringify({'name': name})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hideAllSection(section2);
                } else {
                    const errorText = data.error || 'Произошла ошибка';
                    showError(section1, errorText);
                }
            })
            .catch(error => {
                showError(section1, 'Ошибка соединения с сервером');
            });
    });

    section1.querySelector('.prev').addEventListener('click', function () {
        window.location.href = '/constructor/';
    });


    section2.querySelector('#value_add').addEventListener('click', function () {
        const parent = section2.querySelector('#columns')

        let child = document.createElement('div')
        child.classList.add('col')
        child.innerHTML = `
            <label for="col-name">Имя столбца</label>
            <input type="text" name="col-name" class="col-name form-control">
            <label for="datatype-select">Тип данных:</label>
            <select name="datatype-select" class="form-select datatype-select">
                <option value="int">int64</option>
                <option value="string">string</option>
                <option value="float">float64</option>
            </select>
            <input style="margin-top: 10px" class="rem btn btn-danger" type="button" value="Удалить">
        `
        child.querySelector('.rem').addEventListener('click', function () {
            child.remove()
        })
        parent.appendChild(child)
    })

    section2.querySelector('.next').addEventListener('click', function () {
        let columns = section2.querySelectorAll('.col')
        let error;
        let data = []
        if (columns.length < 2){
            showError(section2, 'Минимум 2 столбца')
            error = true
        }
        columns.forEach(col => {
            let name = col.querySelector('.col-name').value
            let dt = col.querySelector('.datatype-select').value
            const firstChar = name.trim().charAt(0);


            if (!/^[a-zA-Z]$/.test(firstChar)) {
                showError(section2, `В столбце "${col.value}" название должно начинаться с буквы`);
                error = true
                return false
            }
            if (!/^[a-zA-Z0-9]+$/.test(name)){
                showError(section2, 'Название столбца должно быть из английских букв и цифр')
                error = true
                return false
            }
            let col_data = {
                'name': name,
                'datatype': dt
            }
            data.push(col_data)
        });

        if (!error){
            hideAllSection(section3)
        }

    });

    section2.querySelector('.prev').addEventListener('click', function () {
        hideAllSection(section1)
    });
});
