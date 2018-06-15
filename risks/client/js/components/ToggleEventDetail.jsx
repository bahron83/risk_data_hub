const React = require('react');
const {Tooltip, OverlayTrigger} = require('react-bootstrap');

const ToggleEventDetail = React.createClass({
    propTypes: {
            toggleEventDetail: React.PropTypes.func,
            showEventDetail: React.PropTypes.bool,
            show: React.PropTypes.bool
    },                
    render() {
        const {toggleEventDetail, showEventDetail, show} = this.props;
        const icon = showEventDetail ? "times" : "bar-chart";
        const label = showEventDetail ? "Disable Event details view" : "Enable Event details view";
        const tooltip = (<Tooltip id={"tooltip-sub-value"} className="disaster">{label}</Tooltip>);
        return show ? (
            <OverlayTrigger placement="bottom" overlay={tooltip}>
                <button id="disaster-sub-units-button" className="btn btn-primary" onClick={toggleEventDetail}>
                    <i className={"fa fa-" + icon}/>
                </button>
            </OverlayTrigger>
        ) : null;
    }
});

module.exports = ToggleEventDetail;