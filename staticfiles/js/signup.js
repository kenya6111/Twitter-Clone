document.addEventListener('DOMContentLoaded',function(){
    // 選択肢（年）を生成
    const selectYear = document.getElementById("select-year")
    for(let i =2020;i>1940;i--){
        const newOption = document.createElement("option");
        newOption.setAttribute("value",i)
        newOption.setAttribute("type","hidden")
        newOption.textContent = i
        selectYear.appendChild(newOption)
    }
    
    // 選択肢（月）を生成
    const selectMonth = document.getElementById("select-month")
    for(let i =1;i<=12;i++){
        const newOption = document.createElement("option");
        newOption.setAttribute("value",i)
        // newOption.setAttribute("type","hidden")
        newOption.textContent = i
        selectMonth.appendChild(newOption)
    }
    
    // 選択肢（日）を取得
    const selectDay = document.getElementById("select-day")
    for(let i =1;i<=31;i++){
        const newOption = document.createElement("option");
        newOption.setAttribute("value",i)
        // newOption.setAttribute("type","hidden")
        newOption.textContent = i
        selectDay.appendChild(newOption)
    }

    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
        }

        form.classList.add('was-validated')
        }, false)
    })

})