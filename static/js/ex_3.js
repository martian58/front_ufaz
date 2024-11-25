function luhnCheck(cardNumber) {
    const digits = cardNumber.toString().split('').map(Number).reverse();
    let sum = 0;
  
    digits.forEach((digit, index) => {
      if (index % 2 === 1) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      sum += digit;
    });
  
    if (sum % 10 === 0) {
      console.log(`${cardNumber} is Valid`);
    } else {
      console.log(`${cardNumber} is Invalid`);
    }
  }
  
  luhnCheck(4532015112830366); 
  