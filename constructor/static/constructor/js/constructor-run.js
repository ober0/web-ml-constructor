document.addEventListener('DOMContentLoaded', function () {
    const section1 = document.getElementById('name-section');
    const section2 = document.getElementById('list-section');
    const section3 = document.getElementById('df-section');
    const section4 = document.getElementById('wait-section');

    const sections = [section1, section2, section3, section4];


    let DATA = []
    let NAME = []

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
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({'name': name})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hideAllSection(section2);
                    NAME = name
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

        const currentIndex = parent.children.length;

        let child = document.createElement('div')
        child.classList.add('col')
        child.innerHTML = `
            <label for="col-name">Имя столбца</label>
            <input type="text" name="col-name" class="col-name form-control">
            <label for="datatype-select">Тип данных:</label>
            <select name="datatype-select" class="form-select datatype-select">
                <option value="int64">int64</option>
                <option value="object">object</option>
                <option value="float64">float64</option>
            </select>
            
            <div style="margin-top: 10px" class="predict-val">
                <input class="form-check-input" type="radio" name="options" id="option-${currentIndex}" value="option-${currentIndex}" checked>
                <label class="form-check-label" for="option-${currentIndex}">
                    Предсказывать это значение
                </label>
            </div>
            
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
        if (columns.length < 2){
            showError(section2, 'Минимум 2 столбца')
            error = true
        }
        let index = 0
        console.log(columns.length)
        columns.forEach(col => {
            let name = col.querySelector('.col-name').value
            let dt = col.querySelector('.datatype-select').value
            const firstChar = name.trim().charAt(0);


            if (!/^[a-zA-Z]$/.test(firstChar)) {
                showError(section2, `В столбце "${col.value}" название должно начинаться с буквы`);
                error = true
                return false
            }
            if (!/^[a-zA-Z0-9\s!@#$%^&*()_,.?":{}\|/<>]+$/.test(name)) {
                showError(section2, 'Название столбца должно быть из английских букв и цифр')
                error = true
                return false
            }

            let selector = col.querySelector('input[name="options"]')

            let col_data = {
                'name': name,
                'datatype': dt,
                'predict': selector.checked ? 'True' : 'False'
            }
            DATA.push(col_data)
            index++
        });

        if (!error){
            hideAllSection(section3)
        }
        else {
            DATA = []
        }

    });

    section2.querySelector('.prev').addEventListener('click', function () {
        hideAllSection(section1)
    });



    section3.querySelector('.next').addEventListener('click', function () {
        let fileLoad = section3.querySelector('#dataset').files[0]
        if (fileLoad){
            if (fileLoad.type === 'text/csv'){
                hideAllSection(section4)
                const formData = new FormData();
                formData.append('file', fileLoad)
                formData.append('name', NAME)
                formData.append('data', JSON.stringify(DATA))
                console.log(NAME, DATA, fileLoad)
                fetch('/constructor/model/check/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.messages)
                        let messages = Object.values(data.messages)
                        console.log(messages)

                        const parent = document.getElementById('info')

                        messages.forEach(message => {
                            const time = message['time']
                            const text = message['text']
                            const color = message['color']
                            let new_message = document.createElement('div')
                            new_message.classList.add('logs-message')
                            new_message.style.color = color
                            new_message.innerHTML = `
                                <p>${time} ${text}</p>
                            `
                            parent.appendChild(new_message)
                        })
                        if (data.success){
                            const modelId = data.modelId
                            let formData = new FormData()
                            formData.append('modelId', modelId)
                            fetch('/constructor/model/create/', {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                },
                                body: formData
                            })
                                .then(response => response.json())
                                .then(data => {
                                    console.log(data)
                                    let messages = Object.values(data.messages)
                                    console.log(messages)

                                    const parent = document.getElementById('info')

                                    messages.forEach(message => {
                                        const time = message['time']
                                        const text = message['text']
                                        const color = message['color']
                                        let new_message = document.createElement('div')
                                        new_message.classList.add('logs-message')
                                        new_message.style.color = color
                                        new_message.innerHTML = `
                                            <p>${time} ${text}</p>
                                        `
                                        parent.appendChild(new_message)
                                    })

                                    let graph = document.createElement('img')
                                    graph.classList.add('img-graph')
                                    graph.src = '/static/graphics/' + data.graphicsPath + ".png"
                                    console.log('/static/graphics/' + data.graphicsPath + ".png")
                                    parent.appendChild(graph)
                                    document.getElementById('wait-section-text').remove()
                                    if (!data.success){
                                        document.getElementById('stop-req').style.display = 'block'
                                    }
                                    else {

                                    }
                                })
                        }
                        else {
                            document.getElementById('stop-req').style.display = 'block'
                            document.getElementById('wait-section-text').remove()
                        }

                    })
            }
            else {
                showError(section3, 'Неверный формат файла')
            }
        }
        else {
            showError(section3, 'Загрузите датасет')
        }


    });

    section4.querySelector('.prev').addEventListener('click', function () {
        hideAllSection(section3)
    });

    section3.querySelector('.prev').addEventListener('click', function () {
        DATA = []
        hideAllSection(section2)
    });



});
