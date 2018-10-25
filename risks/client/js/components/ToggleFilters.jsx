const React = require('react');
const {Tooltip, OverlayTrigger} = require('react-bootstrap');

const ToggleFilters = React.createClass({
    propTypes: {
        toggleFiltersVisibility: React.PropTypes.func,
            showFilters: React.PropTypes.bool            
    },                
    render() {
        const {toggleFiltersVisibility, showFilters} = this.props;
        const icon = "filter";
        const label = showFilters ? "Hide filters" : "View filters";
        const tooltip = (<Tooltip id={"tooltip-sub-value"} className="disaster">{label}</Tooltip>);
        return (
            <OverlayTrigger placement="bottom" overlay={tooltip}>
                <button id="disaster-filters-button" className="btn btn-primary" onClick={toggleFiltersVisibility}>
                    <i className={"fa fa-" + icon}/>
                </button>
            </OverlayTrigger>
        )
    }
});

module.exports = ToggleFilters;