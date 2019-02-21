const React = require('react');
const {connect} = require('react-redux');
const Navigation = require('./Navigation');
const HelpBtn = require('./HelpBtn');

const {shareUrlSelector} = require('../selectors/disaster');
const SharingLink = connect(shareUrlSelector)(require('./ShareLink'));
const TopBar = React.createClass({
    propTypes: {
        navItems: React.PropTypes.array,        
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
            getData: () => {},
            title: ''
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
        const {navItems, context, activeRisk, zoom, toggleTutorial, showHazard} = this.props;  
        const iconClass = activeRisk.mnemonic ? `icon-${activeRisk.mnemonic.toLowerCase()}` : 'icon-overview';
        return (            
                <div className="disaster-breadcrumbs">                    
                    <ul className="nav nav-pills disaster-breadcrumbs" role="tablist">
                        {showHazard ? this.getItems() : null}
                    </ul>
                    <Navigation items={navItems} zoom={zoom} context={context}/>
                    <div id="disaster-page-tools" className="pull-right btn-group">
                        <SharingLink bsSize=""/>
                        <HelpBtn toggleTutorial={toggleTutorial}/>
                    </div>
                </div>                            
        );        
    }
});
//<span className="active-risk"><i className={iconClass}></i>{activeRisk.description || 'Overview'}</span>
module.exports = TopBar;
