import { connect } from 'react-redux';
import { admDivisionLookup, applyFilters } from '../actions/disaster';
import { lookupResultsSelector } from '../selectors/disaster';

const SearchPlugin = connect(
    lookupResultsSelector,
    {
        admDivisionLookup,
        applyFilters
    }
)(require('../components/SearchLocation'));

module.exports = {
    SearchPlugin,
    reducers: {}
};