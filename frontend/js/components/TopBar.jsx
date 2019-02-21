/**
 * Copyright 2017, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const {connect} = require('react-redux');
const Navigation = require('./Navigation');
const HelpBtn = require('./HelpBtn');

const RiskSelector = require('./RiskSelector');
import SearchLocation from './SearchLocation';
const {shareUrlSelector} = require('../selectors/disaster');
const SharingLink = connect(shareUrlSelector)(require('./ShareLink'));
const TopBar = React.createClass({
    propTypes: {
        navItems: React.PropTypes.array,
        //riskItems: React.PropTypes.array,
        getData: React.PropTypes.func,
        zoom: React.PropTypes.func,
        activeRisk: React.PropTypes.object,
        overviewHref: React.PropTypes.string,
        title: React.PropTypes.string.isRequired,
        context: React.PropTypes.string,
        toggleTutorial: () => {}
    },
    getDefaultProps() {
        return {
            navItems: [],
            //riskItems: [],
            getData: () => {},
            title: ''
        };
    },
    render() {        
        const {navItems, context, overviewHref, activeRisk, getData, zoom, toggleTutorial} = this.props;  
        const iconClass = activeRisk.mnemonic ? `icon-${activeRisk.mnemonic.toLowerCase()}` : 'icon-overview';
        return (
            <div className="container-fluid">
                <div id="main-search-widget" className="search-box">
                    <SearchLocation />
                </div>
                <div className="disaster-breadcrumbs">
                    <span className="active-risk"><i className={iconClass}></i>{activeRisk.description || 'Overview'}</span>
                    <Navigation items={navItems} zoom={zoom} context={context}/>
                    <div id="disaster-page-tools" className="pull-right btn-group">
                        <SharingLink bsSize=""/>
                        <HelpBtn toggleTutorial={toggleTutorial}/>
                    </div>
                </div>                
            </div>
        );        
    }
});

/*removed
<div id="disaster-risk-selector-menu" className="disaster-risk-selector">
                    <RiskSelector riskItems={riskItems} overviewHref={overviewHref} activeRisk={activeRisk} getData={getData}/>
                </div>
*/

module.exports = TopBar;
