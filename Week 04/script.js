const scoreInput = document.getElementById('scoreInput');
const calcBtn = document.getElementById('calcBtn');
const resultDiv = document.getElementById('result');

calcBtn.addEventListener('click',function() {
    let score =Number(scoreInput.value);

    if(isNaN(score) || score < 0 || score > 100) {
         resultDiv.innerHTML = 'Please enter a valid score between 0 and 100.';
         resultDiv.style.color = 'red';
         return;
    }
//display the grade based on the score
    let grade = '';

    if(score >= 70) {
        grade = 'A';
    } 
    else if(score >= 60) {
        grade = 'B';
    } 
    else if(score >= 50) {
        grade = 'C';
    } 
    else if(score >= 40) {
        grade = 'D';
    }
    else {
        grade = 'F';
    }

    resultDiv.innerHTML = `Your grade is: ${grade}`;
    
    if(grade === 'A') {
        resultDiv.style.color = 'green';
    }
    else if(grade === 'B') {
        resultDiv.style.color = 'blue';
    }
    else if(grade === 'C') {
        resultDiv.style.color = 'orange';
    }
    else if(grade === 'D') {
        resultDiv.style.color = 'yellow';
    }
    else {
        resultDiv.style.color = 'red';
    }

    scoreInput.value = '';
    scoreInput.focus();

});
