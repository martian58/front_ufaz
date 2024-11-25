// Helper function to calculate the cube of a number
const cube = (n) => Math.pow(n, 3);

// Helper function to calculate ABC from A, B, C
const calculateABC = (A, B, C) => A * 100 + B * 10 + C;

// Helper function to calculate A^3 + B^3 + C^3
const calculateCubicSum = (A, B, C) => cube(A) + cube(B) + cube(C);

// Create an array with numbers from 1 to 9
const digits = Array.from({ length: 9 }, (_, i) => i + 1);

// Iterate over all possible combinations of A, B, C using forEach
digits.forEach((A) => {
  digits.forEach((B) => {
    digits.forEach((C) => {
      const ABC = calculateABC(A, B, C);
      const cubicSum = calculateCubicSum(A, B, C);

      // Check if the number ABC equals the sum of cubes of A, B, C
      if (ABC === cubicSum) {
        console.log(`Found a match! A = ${A}, B = ${B}, C = ${C} => ABC = ${ABC}, A^3 + B^3 + C^3 = ${cubicSum}`);
      }
    });
  });
});
