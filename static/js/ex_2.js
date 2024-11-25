function giveChange(amount) {
    const banknotes = [200, 100, 50, 20, 10, 5, 1];
    const change = {};
  
    banknotes.forEach(function(note) {
      let count = Math.floor(amount / note);
      if (count > 0) {
        change[note] = count;
      }
      amount %= note;
    });
  
    console.log(`Change breakdown: `, change);
  }
  
  giveChange(369);
  