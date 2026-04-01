const schoolType = document.getElementById('id_school_type')
const gradeField = document.getElementById('grade-field')
const gradeSelect = document.getElementById('id_grade')

schoolType.addEventListener('change', function() {
    const value = parseInt(this.value)

    if (!value) {
        gradeField.style.display = 'none'
        gradeSelect.innerHTML = ''
        return
    }

    const grades = GRADE_CHOICES[value]
    gradeSelect.innerHTML = '<option value="">---------</option>'

    grades.forEach(([id, label]) => {
        const option = document.createElement('option')
        option.value = id
        option.textContent = label
        gradeSelect.appendChild(option)
    })

    gradeField.style.display = 'block'
})