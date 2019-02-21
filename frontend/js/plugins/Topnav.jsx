import { connect } from 'react-redux';
import { getData, zoomInOut } from '../actions/disaster';
import { topBarSelector } from '../selectors/disaster';
import { toggleControl } from '../../MapStore2/web/client/actions/controls';

const TopnavPlugin = connect(
    topBarSelector,    
    {        
        getData,
        zoom: zoomInOut,
        toggleTutorial: toggleControl.bind(null, 'tutorial', null)        
    }
)(require('../components/TopNav'));

module.exports = {
    TopnavPlugin,
    reducers: {}
};