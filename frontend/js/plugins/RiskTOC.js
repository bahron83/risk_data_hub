/**
 * Copyright 2016, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const PropTypes = require('prop-types');
const ReactDOM = require('react-dom');
const {connect} = require('react-redux');
const {createSelector} = require('reselect');

const {changeLayerProperties, changeGroupProperties, toggleNode,
       sortNode, showSettings, hideSettings, updateSettings, updateNode, removeNode} = require('../../MapStore2/web/client/actions/layers');
const {getLayerCapabilities} = require('../../MapStore2/web/client/actions/layerCapabilities');
const {zoomToExtent} = require('../../MapStore2/web/client/actions/map');
const {groupsSelector} = require('../../MapStore2/web/client/selectors/layers');

const LayersUtils = require('../../MapStore2/web/client/utils/LayersUtils');

const Message = require('../../MapStore2/web/client/plugins/locale/Message');

const tocSelector = createSelector(
    [
        (state) => state.controls && state.controls.toolbar && state.controls.toolbar.active === 'toc',
        groupsSelector,
        (state) => state.layers && state.layers.settings || {expanded: false, options: {opacity: 1}},
        (state) => state.controls && state.controls.queryPanel && state.controls.queryPanel.enabled || false
    ], (enabled, groups, settings, querypanelEnabled) => ({
        enabled,
        groups,
        settings,
        querypanelEnabled
    })
);

const TOC = require('../../MapStore2/web/client/components/TOC/TOC');
const DefaultGroup = require('../../MapStore2/web/client/components/TOC/DefaultGroup');
const DefaultLayer = require('../../MapStore2/web/client/components/TOC/DefaultLayer');
const DefaultLayerOrGroup = require('../../MapStore2/web/client/components/TOC/DefaultLayerOrGroup');

class LayerTree extends React.Component{
    static propTypes = {
        id: PropTypes.number,
        buttonContent: PropTypes.node,
        groups: PropTypes.array,
        settings: PropTypes.object,
        querypanelEnabled: PropTypes.bool,
        groupStyle: PropTypes.object,
        groupPropertiesChangeHandler: PropTypes.func,
        layerPropertiesChangeHandler: PropTypes.func,
        onToggleGroup: PropTypes.func,
        onToggleLayer: PropTypes.func,
        onToggleQuery: PropTypes.func,
        onZoomToExtent: PropTypes.func,
        retrieveLayerData: PropTypes.func,
        onSort: PropTypes.func,
        onSettings: PropTypes.func,
        hideSettings: PropTypes.func,
        updateSettings: PropTypes.func,
        updateNode: PropTypes.func,
        removeNode: PropTypes.func,
        activateRemoveLayer: PropTypes.bool,
        activateLegendTool: PropTypes.bool,
        activateZoomTool: PropTypes.bool,
        activateQueryTool: PropTypes.bool,
        activateSettingsTool: PropTypes.bool,
        visibilityCheckType: PropTypes.string,
        settingsOptions: PropTypes.object,
        enabled: PropTypes.bool
    }
    static defaultProps = {                
        groupPropertiesChangeHandler: () => {},
        layerPropertiesChangeHandler: () => {},
        retrieveLayerData: () => {},
        onToggleGroup: () => {},
        onToggleLayer: () => {},
        onToggleQuery: () => {},
        onZoomToExtent: () => {},
        onSettings: () => {},
        updateNode: () => {},
        removeNode: () => {},
        activateLegendTool: false,
        activateZoomTool: false,
        activateSettingsTool: false,
        activateRemoveLayer: false,
        activateQueryTool: false,
        visibilityCheckType: "glyph",
        settingsOptions: {
            includeCloseButton: false,
            closeGlyph: "1-close",
            asModal: false,
            buttonSize: "small"
        },
        querypanelEnabled: false        
    }
    getNoBackgroundLayers(group) {
        return group.name !== 'background';
    }
    renderTOC() {           
        const Group = (<DefaultGroup onSort={this.props.onSort}
                                  propertiesChangeHandler={this.props.groupPropertiesChangeHandler}
                                  onToggle={this.props.onToggleGroup}
                                  style={this.props.groupStyle}
                                  groupVisibilityCheckbox={true}
                                  visibilityCheckType={this.props.visibilityCheckType}
                                  />);
        const Layer = (<DefaultLayer
                            settingsOptions={this.props.settingsOptions}
                            onToggle={this.props.onToggleLayer}
                            onToggleQuerypanel={this.props.onToggleQuery }
                            onZoom={this.props.onZoomToExtent}
                            onSettings={this.props.onSettings}
                            propertiesChangeHandler={this.props.layerPropertiesChangeHandler}
                            hideSettings={this.props.hideSettings}
                            settings={this.props.settings}
                            updateSettings={this.props.updateSettings}
                            updateNode={this.props.updateNode}
                            removeNode={this.props.removeNode}
                            visibilityCheckType={this.props.visibilityCheckType}
                            activateRemoveLayer={this.props.activateRemoveLayer}
                            activateLegendTool={this.props.activateLegendTool}
                            activateZoomTool={this.props.activateZoomTool}
                            activateQueryTool={this.props.activateQueryTool}
                            activateSettingsTool={this.props.activateSettingsTool}
                            retrieveLayerData={this.props.retrieveLayerData}
                            settingsText={<Message msgId="layerProperties.windowTitle"/>}
                            opacityText={<Message msgId="opacity"/>}
                            saveText={<Message msgId="save"/>}
                            closeText={<Message msgId="close"/>}
                            groups={this.props.groups}/>);                
        return (
            <div className="risk-toc-container">
                <TOC onSort={this.props.onSort} filter={this.getNoBackgroundLayers}
                    nodes={this.props.groups}>
                    <DefaultLayerOrGroup groupElement={Group} layerElement={Layer}/>
                </TOC>
            </div>
        );
    }
    render() {   
        console.log('riskTOC props', this.props);
        if (!this.props.groups || !this.props.enabled) {
            return null;
        }
        return this.renderTOC();
    }
    componentDidMount() {               
        this.componentDidUpdate();
    }
    componentDidUpdate() {                
        const overlays = this.props.groups.filter(item => { return item.id === 'Gis Overlays' });
        if(ReactDOM.findDOMNode(this) !== null) {  
            var layers = ReactDOM.findDOMNode(this).getElementsByClassName('toc-title');
            for (var i=0;i<layers.length;i++) {
                var isGisOverlay = (layers[i].innerHTML != 'Admins units' && layers[i].innerHTML.indexOf('_analysis') < 0);
                if(layers[i].parentNode.getElementsByClassName('linkto-layer-details').length == 0 && isGisOverlay) {
                    var link = document.createElement('a');
                    const contextUrl = window.location.pathname.indexOf('risk-data-hub') !== -1 ? '/risk-data-hub' : '';
                    let layerName = "";                    
                    overlays[0]['nodes'].map(v => {
                        if(v && v.title == layers[i].innerHTML)
                            layerName = v && v.name;
                    });
                    link.setAttribute('href', window.location.origin + contextUrl + '/layers/' + layerName);
                    link.setAttribute('target', '_blank');
                    link.setAttribute('class', 'linkto-layer-details');
                    link.innerHTML = 'Open details';
                    layers[i].parentNode.appendChild(link);
                }
                
            }
        }                
    }
}

const TOCPlugin = connect(tocSelector, {
    groupPropertiesChangeHandler: changeGroupProperties,
    layerPropertiesChangeHandler: changeLayerProperties,
    retrieveLayerData: getLayerCapabilities,
    onToggleGroup: LayersUtils.toggleByType('groups', toggleNode),
    onToggleLayer: LayersUtils.toggleByType('layers', toggleNode),
    onSort: LayersUtils.sortUsing(LayersUtils.sortLayers, sortNode),
    onSettings: showSettings,
    onZoomToExtent: zoomToExtent,
    hideSettings,
    updateSettings,
    updateNode,
    removeNode
})(LayerTree);

module.exports = {
    TOCPlugin
};
