package com.example.abaland.android_remote;

import android.view.View;

import android.widget.*;

import java.util.HashMap;
import java.util.Locale;

class AirconControls extends GenericRemoteControls {

    private MainActivity activity;

    // GUI Objects
    private Switch airconStateSwitch;
    private RadioGroup airconTargetRadio;
    private RadioGroup airconModeRadio;
    private SeekBar airconTemperatureSeekBar;
    private TextView airconTemperatureText;
    private Spinner fanSpeedSpinner;
    private Spinner fanDirectionSpinner;
    private Button sendButton;

    // Defaults values/indexes
    private boolean airconState = true;
    private Integer airconTargetIndex = 0; // 0: living, 1: bedroom
    private Integer airconModeIndex = 0; // 0: heat, 1: dry, 2: cold.
    private Integer airconTemperature = 24;
    private Integer fanSpeedIndex = 0; // 0: auto, 1: weak, 2: middle, 3: strong
    private Integer fanDirectionIndex = 0; //0:auto, 1:loop, 2:lowest, 3:low, 4:middle, 5:high, 6:highest

    // Mapping from index to value.
    private HashMap<Boolean, String> airconStateMapping = new HashMap<>();

    private String[] airconTargetMapping = {"living", "bedroom"};
    private String[] airconModeMapping = {"heat", "dry", "cool"};
    private String[] fanSpeedMapping = {"auto", "weak", "middle", "strong"};
    private String[] fanDirectionMapping = {"auto", "loop", "lowest", "low", "middle", "high",
            "highest"};


    AirconControls (MainActivity activity) {

        this.activity = activity;
    }

    /**
     * Querries aircon target radiobutton from aircon GUI to get which aircon signal must be sent to
     *
     * @return {'bedroom', 'living'}
     */
    private String getAirconTarget(){

        ///////////////////////////////////////////////////
        return airconTargetMapping[airconTargetIndex];
        ///////////////////////////////////////////////////

    }


    /**
     * Querries all elements from aircon GUI to get related configuration as a string.
     *
     * @return Comma-separated aircon configuration, following syntax of "on,heat,25,strong,loop"
     */
    private String getConfigAsString(){

        String fullConfig = "";

        // Updates GUI correctly based on defaults
        fullConfig += airconStateMapping.get(airconState) + ",";
        fullConfig += airconModeMapping[airconModeIndex] + ",";
        fullConfig += String.valueOf(airconTemperature) + ",";
        fullConfig += fanSpeedMapping[fanSpeedIndex] + ",";
        fullConfig += fanDirectionMapping[fanDirectionIndex];

        ///////////////////
        return fullConfig;
        ///////////////////

    }


    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        airconStateSwitch = (Switch) this.activity.findViewById(R.id.Aircon_Power);
        airconTargetRadio = (RadioGroup) this.activity.findViewById(R.id.Aircon_Target);
        airconModeRadio = (RadioGroup) this.activity.findViewById(R.id.Aircon_Mode);
        airconTemperatureSeekBar = (SeekBar) this.activity.findViewById(R.id.Aircon_Temperature);
        airconTemperatureText = (TextView) this.activity.findViewById(R.id.Aircon_Temperature_Text);
        fanSpeedSpinner = (Spinner) this.activity.findViewById(R.id.Aircon_Speed);
        fanDirectionSpinner = (Spinner) this.activity.findViewById(R.id.Aircon_Direction);
        sendButton = (Button) this.activity.findViewById(R.id.Send_Aircon_Signal);

    }


    /**
     * Initializes values from GUI elements. Uses default value defined above.
     *
     * TODO : add User preferences to default
     */
    private void initializeGUIValues() {

        // Turns On/Off switch
        airconStateSwitch.setChecked(airconState);

        // Checks correct aircon mode
        switch (airconModeIndex) {

            case  0:

                airconModeRadio.check(R.id.Aircon_Heater);
                break;

            case 1:

                airconModeRadio.check(R.id.Aircon_Dry);
                break;

            case 2:

                airconModeRadio.check(R.id.Aircon_Cooler);
                break;

        }

        // Checks correct aircon target
        switch (airconTargetIndex) {

            case  0:

                airconTargetRadio.check(R.id.Aircon_Living);
                break;

            case 1:

                airconTargetRadio.check(R.id.Aircon_Bedroom);
                break;

        }


        // Sets progress bar for temperature. Converts from real [16, 31] range to GUI [0, 15].
        airconTemperatureSeekBar.setProgress(airconTemperature - 16);
        airconTemperatureText.setText(String.format(Locale.US, "%d", airconTemperature));

        // Assigns both spinners for fan speed/direction.
        fanSpeedSpinner.setSelection(fanSpeedIndex);
        fanDirectionSpinner.setSelection(fanDirectionIndex);

    }


    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        // Adds listener to On/Off state switch (updates airconState)
        airconStateSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {

                // Updates internal parameter
                airconState = isChecked;

            }

        });


        // Adds listener for aircon target radio buttons.
        airconTargetRadio.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged (RadioGroup group, int checkedId){

                // Updates internal parameter
                switch(checkedId) {

                    case R.id.Aircon_Living:

                        airconTargetIndex = 0;
                        break;

                    case R.id.Aircon_Bedroom:

                        airconTargetIndex = 1;
                        break;

                }

            }

        });


        // Adds listener for aircon mode radio buttons.
        airconModeRadio.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged (RadioGroup group, int checkedId){

                // Updates internal parameter
                switch(checkedId) {

                    case R.id.Aircon_Heater:

                        airconModeIndex = 0;
                        break;

                    case R.id.Aircon_Dry:

                        airconModeIndex = 1;
                        break;

                    case R.id.Aircon_Cooler:

                        airconModeIndex = 2;
                        break;

                }

            }

        });


        // Adds listener for aircon temperature seekbar
        airconTemperatureSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {

                // Updates internal parameter
                airconTemperature = progress + 16;

                // Updates text GUI element with current temperature
                airconTemperatureText.setText(String.valueOf(airconTemperature));

            }

        });


        // Adds listener for the fan speed spinner
        fanSpeedSpinner.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView,
                                       int position, long id) {

                // Updates internal parameter
                fanSpeedIndex = position;

            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {}

        });


        // Adds listener for the fan direction spinner
        fanDirectionSpinner.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView,
                                       int position, long id) {

                // Updates internal parameter
                fanDirectionIndex = position;

            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {}

        });


        // Adds listener for configuration send button
        sendButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){

                String remoteName = "aircon_" + getAirconTarget();
                MainActivity activity = AirconControls.this.activity;
                String messageToSend = convertToXmlInstruction(remoteName, getConfigAsString());
                activity.rabbitManager.askWorker("remote_control", messageToSend, activity);

            }

        });
    }


    void initialize() {

        // Initializes the mapping of index-to-value for the only hashmap existing
        airconStateMapping.put(false, "off");
        airconStateMapping.put(true, "on");

        // Links all GUI items to the script
        bindGUIToScript();

        // Updates GUI correctly based on defaults
        initializeGUIValues();

        // Adds listeners to GUI, to update internal parameters/take appropriate actions on change
        addGUIListeners();

    }

}
