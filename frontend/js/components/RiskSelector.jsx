/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');

const RiskSelector = React.createClass({
    propTypes: {
        riskItems: React.PropTypes.object,
        overviewHref: React.PropTypes.string,
        activeRisk: React.PropTypes.object,
        getData: React.PropTypes.func
    },
    getDefaultProps() {
        return {
            getData: () => {}
        };
    },
    getItems() {
        const {riskItems, activeRisk, getData, overviewHref} = this.props;
        let riskItem = [];
        riskItems['hazardType'].map(r => {
            if(r.mnemonic == activeRisk.mnemonic)
                riskItem.push(r);
        })
        const items = [{
                    "mnemonic": "Overview",
                    "title": "Overview",
                    "riskAnalysis": 1,
                    "href": overviewHref
            }, ...riskItem];
        return items.map((item, idx) => {
            const {title, href, riskAnalysis, mnemonic} = item;
            const active = activeRisk.mnemonic === mnemonic;
            const noData = !(riskAnalysis > 0);
            return (
            <li key={idx} className={`${noData ? 'no-data disabled' : ''} text-center  ${active ? 'active' : ''}`} onClick={active || noData ? undefined : () => getData(href, true)}>
                  <a href="#" data-toggle="tab">
                    <i className={`icon-${mnemonic.toLowerCase()}`}></i> &nbsp; {title}
                  </a>
            </li>);
        });
    },
    render() {
        const { showHazard } = this.props;
        return (
            <ul className="nav nav-pills disaster-breadcrumbs" role="tablist">
                {showHazard ? this.getItems() : null}
            </ul> );
    }
});

module.exports = RiskSelector;
