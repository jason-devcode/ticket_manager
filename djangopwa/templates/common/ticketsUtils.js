/**
 * Constructs the complete ticket number from the individual digit values.
 * @param {number} digit_1 - The value of the first digit (from left to right).
 * @param {number} digit_2 - The value of the second digit (from left to right).
 * @param {number} digit_3 - The value of the third digit (from left to right).
 * @param {number} digit_4 - The value of the fourth digit (from left to right).
 * @returns {number} The constructed ticket number as an integer.
 */
const buildTicketNumber = (digit_1, digit_2, digit_3, digit_4) => {
  const EXP_DIGIT_4_POSITION = 1000; // same to multiply by 10^3
  const EXP_DIGIT_3_POSITION = 100; // same to multiply by 10^2
  const EXP_DIGIT_2_POSITION = 10; // same to multiply by 10^1
  const EXP_DIGIT_1_POSITION = 1; // same to multiply by 10^0

  const ticket_number =
    digit_4 * EXP_DIGIT_4_POSITION +
    digit_3 * EXP_DIGIT_3_POSITION +
    digit_2 * EXP_DIGIT_2_POSITION +
    digit_1 * EXP_DIGIT_1_POSITION;

  return ticket_number;
};
