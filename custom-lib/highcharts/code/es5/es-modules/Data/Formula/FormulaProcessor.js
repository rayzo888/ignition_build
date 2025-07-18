/* *
 *
 *  (c) 2009-2025 Highsoft AS
 *
 *  License: www.highcharts.com/license
 *
 *  !!!!!!! SOURCE GETS TRANSPILED BY TYPESCRIPT. EDIT TS FILE ONLY. !!!!!!!
 *
 *  Authors:
 *  - Sophie Bremer
 *
 * */
'use strict';
import FormulaTypes from './FormulaTypes.js';
var isFormula = FormulaTypes.isFormula, isFunction = FormulaTypes.isFunction, isOperator = FormulaTypes.isOperator, isRange = FormulaTypes.isRange, isReference = FormulaTypes.isReference, isValue = FormulaTypes.isValue;
/* *
 *
 *  Constants
 *
 * */
var asLogicalStringRegExp = / */;
var MAX_FALSE = Number.MAX_VALUE / 1.000000000001;
var MAX_STRING = Number.MAX_VALUE / 1.000000000002;
var MAX_TRUE = Number.MAX_VALUE;
var operatorPriority = {
    '^': 3,
    '*': 2,
    '/': 2,
    '+': 1,
    '-': 1,
    '=': 0,
    '<': 0,
    '<=': 0,
    '>': 0,
    '>=': 0
};
var processorFunctions = {};
var processorFunctionNameRegExp = /^[A-Z][A-Z\.]*$/;
/* *
 *
 *  Functions
 *
 * */
/**
 * Converts non-number types to logical numbers.
 *
 * @param {Highcharts.FormulaValue} value
 * Value to convert.
 *
 * @return {number}
 * Logical number value. `NaN` if not convertable.
 */
function asLogicalNumber(value) {
    switch (typeof value) {
        case 'boolean':
            return value ? MAX_TRUE : MAX_FALSE;
        case 'string':
            return MAX_STRING;
        case 'number':
            return value;
        default:
            return NaN;
    }
}
/**
 * Converts strings to logical strings, while other types get passed through. In
 * logical strings the space character is the lowest value and letters are case
 * insensitive.
 *
 * @param {Highcharts.FormulaValue} value
 * Value to convert.
 *
 * @return {Highcharts.FormulaValue}
 * Logical string value or passed through value.
 */
function asLogicalString(value) {
    if (typeof value === 'string') {
        return value.toLowerCase().replace(asLogicalStringRegExp, '\0');
    }
    return value;
}
/**
 * Converts non-number types to a logic number.
 *
 * @param {Highcharts.FormulaValue} value
 * Value to convert.
 *
 * @return {number}
 * Number value. `NaN` if not convertable.
 */
function asNumber(value) {
    switch (typeof value) {
        case 'boolean':
            return value ? 1 : 0;
        case 'string':
            return parseFloat(value.replace(',', '.'));
        case 'number':
            return value;
        default:
            return NaN;
    }
}
/**
 * Process a basic operation of two given values.
 *
 * @private
 *
 * @param {Highcharts.FormulaOperator} operator
 * Operator between values.
 *
 * @param {Highcharts.FormulaValue} x
 * First value for operation.
 *
 * @param {Highcharts.FormulaValue} y
 * Second value for operation.
 *
 * @return {Highcharts.FormulaValue}
 * Operation result. `NaN` if operation is not support.
 */
function basicOperation(operator, x, y) {
    switch (operator) {
        case '=':
            return asLogicalString(x) === asLogicalString(y);
        case '<':
            if (typeof x === typeof y) {
                return asLogicalString(x) < asLogicalString(y);
            }
            return asLogicalNumber(x) < asLogicalNumber(y);
        case '<=':
            if (typeof x === typeof y) {
                return asLogicalString(x) <= asLogicalString(y);
            }
            return asLogicalNumber(x) <= asLogicalNumber(y);
        case '>':
            if (typeof x === typeof y) {
                return asLogicalString(x) > asLogicalString(y);
            }
            return asLogicalNumber(x) > asLogicalNumber(y);
        case '>=':
            if (typeof x === typeof y) {
                return asLogicalString(x) >= asLogicalString(y);
            }
            return asLogicalNumber(x) >= asLogicalNumber(y);
    }
    x = asNumber(x);
    y = asNumber(y);
    var result;
    switch (operator) {
        case '+':
            result = x + y;
            break;
        case '-':
            result = x - y;
            break;
        case '*':
            result = x * y;
            break;
        case '/':
            result = x / y;
            break;
        case '^':
            result = Math.pow(x, y);
            break;
        default:
            return NaN;
    }
    // Limit decimal to 9 digits
    return (result % 1 ?
        Math.round(result * 1000000000) / 1000000000 :
        result);
}
/**
 * Converts an argument to Value and in case of a range to an array of Values.
 *
 * @function Highcharts.Formula.getArgumentValue
 *
 * @param {Highcharts.FormulaRange|Highcharts.FormulaTerm} arg
 * Formula range or term to convert.
 *
 * @param {Highcharts.DataTable} [table]
 * Table to use for references and ranges.
 *
 * @return {Highcharts.FormulaValue|Array<Highcharts.FormulaValue>}
 * Converted value.
 */
function getArgumentValue(arg, table) {
    // Add value
    if (isValue(arg)) {
        return arg;
    }
    // Add values of a range
    if (isRange(arg)) {
        return (table && getRangeValues(arg, table) || []);
    }
    // Add values of a function
    if (isFunction(arg)) {
        return processFunction(arg, table);
    }
    // Process functions, operations, references with formula processor
    return processFormula((isFormula(arg) ? arg : [arg]), table);
}
/**
 * Converts all arguments to Values and in case of ranges to arrays of Values.
 *
 * @function Highcharts.Formula.getArgumentsValues
 *
 * @param {Highcharts.FormulaArguments} args
 * Formula arguments to convert.
 *
 * @param {Highcharts.DataTable} [table]
 * Table to use for references and ranges.
 *
 * @return {Array<(Highcharts.FormulaValue|Array<Highcharts.FormulaValue>)>}
 * Converted values.
 */
function getArgumentsValues(args, table) {
    var values = [];
    for (var i = 0, iEnd = args.length; i < iEnd; ++i) {
        values.push(getArgumentValue(args[i], table));
    }
    return values;
}
/**
 * Extracts cell values from a table for a given range.
 *
 * @function Highcharts.Formula.getRangeValues
 *
 * @param {Highcharts.FormulaRange} range
 * Formula range to use.
 *
 * @param {Highcharts.DataTable} table
 * Table to extract from.
 *
 * @return {Array<Highcharts.FormulaValue>}
 * Extracted values.
 */
function getRangeValues(range, table) {
    var columnNames = table
        .getColumnNames()
        .slice(range.beginColumn, range.endColumn + 1), values = [];
    for (var i = 0, iEnd = columnNames.length, cell = void 0; i < iEnd; ++i) {
        var cells = table.getColumn(columnNames[i], true) || [];
        for (var j = range.beginRow, jEnd = range.endRow + 1; j < jEnd; ++j) {
            cell = cells[j];
            if (typeof cell === 'string' &&
                cell[0] === '=' &&
                table !== table.modified) {
                // Look in the modified table for formula result
                cell = table.modified.getCell(columnNames[i], j);
            }
            values.push(isValue(cell) ? cell : NaN);
        }
    }
    return values;
}
/**
 * Extracts the cell value from a table for a given reference.
 *
 * @private
 *
 * @param {Highcharts.FormulaReference} reference
 * Formula reference to use.
 *
 * @param {Highcharts.DataTable} table
 * Table to extract from.
 *
 * @return {Highcharts.FormulaValue}
 * Extracted value. 'undefined' might also indicate that the cell was not found.
 */
function getReferenceValue(reference, table) {
    var columnName = table.getColumnNames()[reference.column];
    if (columnName) {
        var cell = table.getCell(columnName, reference.row);
        if (typeof cell === 'string' &&
            cell[0] === '=' &&
            table !== table.modified) {
            // Look in the modified table for formula result
            var result = table.modified.getCell(columnName, reference.row);
            return isValue(result) ? result : NaN;
        }
        return isValue(cell) ? cell : NaN;
    }
    return NaN;
}
/**
 * Processes a formula array on the given table. If the formula does not contain
 * references or ranges, then no table has to be provided.
 *
 * @private
 * @function Highcharts.processFormula
 *
 * @param {Highcharts.Formula} formula
 * Formula array to process.
 *
 * @param {Highcharts.DataTable} [table]
 * Table to use for references and ranges.
 *
 * @return {Highcharts.FormulaValue}
 * Result value of the process. `NaN` indicates an error.
 */
function processFormula(formula, table) {
    var x;
    for (var i = 0, iEnd = formula.length, item = void 0, operator = void 0, result = void 0, y = void 0; i < iEnd; ++i) {
        item = formula[i];
        // Remember operator for operation on next item
        if (isOperator(item)) {
            operator = item;
            continue;
        }
        // Next item is a value
        if (isValue(item)) {
            y = item;
            // Next item is a formula and needs to get processed first
        }
        else if (isFormula(item)) {
            y = processFormula(formula, table);
            // Next item is a function call and needs to get processed first
        }
        else if (isFunction(item)) {
            result = processFunction(item, table);
            y = (isValue(result) ? result : NaN); // Arrays are not allowed here
            // Next item is a reference and needs to get resolved
        }
        else if (isReference(item)) {
            y = (table && getReferenceValue(item, table));
        }
        // If we have a next value, lets do the operation
        if (typeof y !== 'undefined') {
            // Next value is our first value
            if (typeof x === 'undefined') {
                if (operator) {
                    x = basicOperation(operator, 0, y);
                }
                else {
                    x = y;
                }
                // Fail fast if no operator available
            }
            else if (!operator) {
                return NaN;
                // Regular next value
            }
            else {
                var operator2 = formula[i + 1];
                if (isOperator(operator2) &&
                    operatorPriority[operator2] > operatorPriority[operator]) {
                    y = basicOperation(operator2, y, processFormula(formula.slice(i + 2)));
                    i = iEnd;
                }
                x = basicOperation(operator, x, y);
            }
            operator = void 0;
            y = void 0;
        }
    }
    return isValue(x) ? x : NaN;
}
/**
 * Process a function on the given table. If the arguments do not contain
 * references or ranges, then no table has to be provided.
 *
 * @private
 *
 * @param {Highcharts.FormulaFunction} formulaFunction
 * Formula function to process.
 *
 * @param {Highcharts.DataTable} [table]
 * Table to use for references and ranges.
 *
 * @param {Highcharts.FormulaReference} [reference]
 * Table cell reference to use for relative references and ranges.
 *
 * @return {Highcharts.FormulaValue|Array<Highcharts.FormulaValue>}
 * Result value (or values) of the process. `NaN` indicates an error.
 */
function processFunction(formulaFunction, table, 
// eslint-disable-next-line @typescript-eslint/no-unused-vars
reference // @todo
) {
    var processor = processorFunctions[formulaFunction.name];
    if (processor) {
        try {
            return processor(formulaFunction.args, table);
        }
        catch (_a) {
            return NaN;
        }
    }
    var error = new Error("Function \"".concat(formulaFunction.name, "\" not found."));
    error.name = 'FormulaProcessError';
    throw error;
}
/**
 * Registers a function for the FormulaProcessor.
 *
 * @param {string} name
 * Name of the function in spreadsheets notation with upper case.
 *
 * @param {Highcharts.FormulaFunction} processorFunction
 * ProcessorFunction for the FormulaProcessor. This is an object so that it
 * can take additional parameter for future validation routines.
 *
 * @return {boolean}
 * Return true, if the ProcessorFunction has been registered.
 */
function registerProcessorFunction(name, processorFunction) {
    return (processorFunctionNameRegExp.test(name) &&
        !processorFunctions[name] &&
        !!(processorFunctions[name] = processorFunction));
}
/**
 * Translates relative references and ranges in-place.
 *
 * @param {Highcharts.Formula} formula
 * Formula to translate references and ranges in.
 *
 * @param {number} [columnDelta=0]
 * Column delta to translate to. Negative translate back.
 *
 * @param {number} [rowDelta=0]
 * Row delta to translate to. Negative numbers translate back.
 *
 * @return {Highcharts.Formula}
 * Formula with translated reference and ranges. This formula is equal to the
 * first argument.
 */
function translateReferences(formula, columnDelta, rowDelta) {
    if (columnDelta === void 0) { columnDelta = 0; }
    if (rowDelta === void 0) { rowDelta = 0; }
    for (var i = 0, iEnd = formula.length, item = void 0; i < iEnd; ++i) {
        item = formula[i];
        if (item instanceof Array) {
            translateReferences(item, columnDelta, rowDelta);
        }
        else if (isFunction(item)) {
            translateReferences(item.args, columnDelta, rowDelta);
        }
        else if (isRange(item)) {
            if (item.beginColumnRelative) {
                item.beginColumn += columnDelta;
            }
            if (item.beginRowRelative) {
                item.beginRow += rowDelta;
            }
            if (item.endColumnRelative) {
                item.endColumn += columnDelta;
            }
            if (item.endRowRelative) {
                item.endRow += rowDelta;
            }
        }
        else if (isReference(item)) {
            if (item.columnRelative) {
                item.column += columnDelta;
            }
            if (item.rowRelative) {
                item.row += rowDelta;
            }
        }
    }
    return formula;
}
/* *
 *
 *  Default Export
 *
 * */
var FormulaProcessor = {
    asNumber: asNumber,
    getArgumentValue: getArgumentValue,
    getArgumentsValues: getArgumentsValues,
    getRangeValues: getRangeValues,
    getReferenceValue: getReferenceValue,
    processFormula: processFormula,
    processorFunctions: processorFunctions,
    registerProcessorFunction: registerProcessorFunction,
    translateReferences: translateReferences
};
export default FormulaProcessor;
