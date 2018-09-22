import React from 'react';
import Input2 from "./Form/Input2";
import Textarea2 from "./Form/Textarea2";
import Date2 from "./Form/Date2";
import {get} from "../gateway";
import * as _ from "underscore";
import Select2 from "./Form/Select2";
import ReactSelect from "react-select";
import ProductAction from "../Models/ProductAction";


const filterAvailableActions = (actions, actionTypes) => {
      return actionTypes.filter(type => -1 === _.findIndex(actions, action => type.id === action.action_id));
};


const filterSelectedActionType = (selectedActionType, availableActionTypes) => {
    if (_.isEmpty(availableActionTypes)) {
        return null;
    }
    if (selectedActionType && -1 !== _.findIndex(availableActionTypes, type => type.id === selectedActionType.id)) {
        return selectedActionType;
    }
    return availableActionTypes[0];
};


const setActionTypes = actionTypes => prevState => {
    const availableActionTypes = filterAvailableActions(prevState.actions, actionTypes);
    const selectedActionType = filterSelectedActionType(prevState.selectedActionType, availableActionTypes);
    return {
        actionTypes,
        availableActionTypes,
        selectedActionType,
    };
};


const productChanged = (prevState, props) => {
    const actions = props.product.actions;
    const availableActionTypes = filterAvailableActions(actions, prevState.actionTypes);
    const selectedActionType = filterSelectedActionType(prevState.selectedActionType, availableActionTypes);
    return {
        actions,
        availableActionTypes,
        selectedActionType,
        saveDisabled: !props.product.canSave(),
    };
};


class ProductForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            actions: [],
            actionTypes: [],
            availableActionTypes: [],
            selectedActionType: null,
            saveDisabled: true,
        };
        get({url: "/webshop/action"}).then(data => this.setState(setActionTypes(data.data)));
    }

    componentDidMount() {
        const {product} = this.props;
        this.unsubscribe = product.subscribe(() => this.setState(productChanged));
    }
    
    componentWillUnmount() {
        this.unsubscribe();
    }
    
    render() {
        const {product, onDelete, onSave} = this.props;
        const {actions, availableActionTypes, selectedActionType, saveDisabled, actionTypes} = this.state;
        
        const actionName = action => (_.find(actionTypes, a => action.action_id === a.id) || {}).name;
        
        const renderAction = (action, i) => (
            <div key={i} className="form-row uk-grid">
                <div className="uk-with-1-6">{actionName(action)}</div>
                <div className="uk-with-1-6"><strong>Värde</strong></div>
                <div className="uk-with-3-6"><Input2 model={action} label={false} formrow={false} name={"value"}/></div>
                <div className="uk-with-1-6">
                    <a className="uk-button uk-button-danger" onClick={() => product.removeAction(action)}><i className="uk-icon-trash-o"/></a>
                </div>
            </div>
        );
        
        return (
            <div className="uk-margin-top">
                <form className="uk-form uk-form-stacked" onSubmit={(e) => {e.preventDefault(); onSave(); return false;}}>
                    <fieldset className="uk-margin-top">
                        <legend><i className="uk-icon-shopping-cart"/> Produkt</legend>
                        <Input2 model={product} name="name" title="Produktnamn" />
                        <Select2 model={product} name="category_id" title="Kategori" getLabel={o => o.name} getValue={o => o.id} dataSource={"/webshop/category"} />
                        <Textarea2 model={product} name="description" title="Beskrivning" rows="4"/>
                        <Input2 model={product} name="unit" title="Enhet" />
                        <Input2 model={product} name="price" title="Pris (SEK)" type="number"/>
                        <Input2 model={product} name="smallest_multiple" title="Multipel " type="number"/>
                    </fieldset>
                    <fieldset className="uk-margin-top">
                        <legend><i className="uk-icon-magic"/> Åtgärder</legend>
                        <div>
                            {actions.map(renderAction)}
                        </div>
                        {
                            _.isEmpty(availableActionTypes)
                            ?
                            ""
                            :
                            <div>
                                <ReactSelect className="uk-width-3-5 uk-float-left"
                                             value={selectedActionType}
                                             options={availableActionTypes}
                                             getOptionValue={o => o.id}
                                             getOptionLabel={o => o.name}
                                             onChange={o=> this.setState({selectedActionType: o})}
                                />
                                <button type="button" className="uk-button uk-button-success uk-float-right" onClick={() => product.addAction(new ProductAction({action_id: selectedActionType.id}))}><i className="uk-icon-plus"/> Lägg till åtgärd</button>
                            </div>
                        }
                    </fieldset>
                    <fieldset className="uk-margin-top">
                        <legend><i className="uk-icon-filter"/> Filter</legend>
                        <Select2 model={product} name="filter" title="Filter" getLabel={o => o.name} getValue={o => o.id} options={[{id: "", name: "No filter"}, {id: "start_package", name: "Startpaket"}]}/>
                    </fieldset>
                    {
                        product.id
                        ?
                        <fieldset className="uk-margin-top">
                            <legend><i className="uk-icon-tag"/> Metadata</legend>
                            <Date2 model={product} name="created_at" title="Skapad"/>
                            <Date2 model={product} name="updated_at" title="Uppdaterad"/>
                        </fieldset>
                        :
                        ""
                    }
                    <fieldset className="uk-margin-top">
                        {product.id ? <a className="uk-button uk-button-danger uk-float-left" onClick={onDelete}><i className="uk-icon-trash"/> Ta bort produkt</a> : ""}
                        <button disabled={saveDisabled} className="uk-button uk-button-success uk-float-right"><i className="uk-icon-save"/> {product.id ? 'Spara' : 'Skapa'}</button>
                    </fieldset>
                </form>
            </div>
        );
    }
}

// TODO Image upload should be supported.


export default ProductForm;
