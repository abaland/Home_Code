package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;
import android.widget.RadioGroup;

import java.util.HashMap;


class LightsControls {

    private MainActivity activity;

    // Mapping from the GUI button text to command name in Python script
    private HashMap<String, String> ButtonToInstructionMapping = new HashMap<>();

    private RadioGroup lightTargetRadio;

    private Integer lightTargetIndex = 0; // 0: living, 1: bedroom

    private String[] lightTargetMapping = {"living", "bedroom"};

    private Button powerButton;
    private Button brightnessDownButton;
    private Button brightnessUpButton;
    private Button brightnessMinButton;
    private Button brightnessMaxButton;


    LightsControls(MainActivity activity) {

        this.activity = activity;

    }


    /**
     * Querries lights target radiobutton from lights GUI to get which lights signal must be sent to
     *
     * @return {'bedroom', 'living'}
     */
    private String getLightTarget(){

        ///////////////////////////////////////////////////
        return lightTargetMapping[lightTargetIndex];
        ///////////////////////////////////////////////////

    }


    /**
     * Applies appropriate function when button on GUI is clicked.
     *
     * Uses text on button and mapping created to get more information about what should be sent.
     *
     * @param v Button clicked, as a View object.
     */
    private void onClickFunction(View v){

        String RemoteName = "light_" + getLightTarget();

        // Casts button clicked as a Button instance, and gets its text content.
        Button clickedButton = (Button) v;
        String ButtonText = clickedButton.getText().toString();

        String KeyToPress = ButtonToInstructionMapping.get(ButtonText);

        MainActivity activity = LightsControls.this.activity;

        activity.rabbitManager.publishMessage(RemoteName, KeyToPress, activity);

    }

    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        lightTargetRadio = (RadioGroup) this.activity.findViewById(R.id.Light_Target);

        powerButton = (Button) this.activity.findViewById(R.id.lights_power);
        brightnessDownButton = (Button) this.activity.findViewById(R.id.darker);
        brightnessUpButton = (Button) this.activity.findViewById(R.id.brighter);
        brightnessMinButton = (Button) this.activity.findViewById(R.id.darkest);
        brightnessMaxButton = (Button) this.activity.findViewById(R.id.brightest);

    }

    /**
     * Initializes values from GUI elements. Uses default value defined above.
     *
     * TODO : add User preferences to default
     */
    private void initializeGUIValues() {

        // Checks correct aircon target
        switch (lightTargetIndex) {

            case  0:

                lightTargetRadio.check(R.id.Light_Living);
                break;

            case 1:

                lightTargetRadio.check(R.id.Light_Bedroom);
                break;

        }

    }


    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        // Adds listener for aircon target radio buttons.
        lightTargetRadio.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {

            @Override
            public void onCheckedChanged (RadioGroup group, int checkedId){

                // Updates internal parameter
                switch(checkedId) {

                    case R.id.Light_Living:

                        lightTargetIndex = 0;
                        break;

                    case R.id.Light_Bedroom:

                        lightTargetIndex = 1;
                        break;

                }

            }

        });

        powerButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        brightnessDownButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        brightnessUpButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        brightnessMinButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        brightnessMaxButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

    }

    void initialize() {

        // Initializes the mapping between text on the buttons and the instruction to send
        ButtonToInstructionMapping.put("Power", "Power");
        ButtonToInstructionMapping.put("Darker", "Bright-");
        ButtonToInstructionMapping.put("Brighter", "Bright+");
        ButtonToInstructionMapping.put("Darkest", "Minimum");
        ButtonToInstructionMapping.put("Brightest", "Maximum");

        // Links all GUI items to the script
        bindGUIToScript();

        // Updates GUI correctly based on defaults
        initializeGUIValues();

        // Adds listeners to GUI, to update internal parameters/take appropriate actions on change
        addGUIListeners();

    }

}
