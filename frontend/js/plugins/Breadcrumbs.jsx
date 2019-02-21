import { connect } from 'react-redux';
import { getData } from '../actions/disaster';
import { topBarSelector } from '../selectors/disaster';

const BreadcrumbsPlugin = connect(
    topBarSelector,
    {
        getData
    }
)(require('../components/RiskSelector'));

module.exports = {
    BreadcrumbsPlugin,
    reducers: {}
};