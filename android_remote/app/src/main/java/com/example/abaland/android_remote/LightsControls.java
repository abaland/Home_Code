package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;

import java.util.HashMap;


class LightsControls {

    private MainActivity activity;

    private HashMap<String, String> ButtonToInstructionMapping = new HashMap<>();

    private Button powerButton;
    private Button brightnessDownButton;
    private Button brightnessUpButton;
    private Button brightnessMinButton;
    private Button brightnessMaxButton;


    LightsControls(MainActivity activity) {

        this.activity = activity;

    }

    /**
     * Applies appropriate function when button on GUI is clicked.
     *
     * Uses text on button and mapping created to get more information about what should be sent.
     *
     * @param v Button clicked, as a View object.
     */
    private void onClickFunction(View v){

        String RemoteName = "tv";

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

        powerButton = (Button) this.activity.findViewById(R.id.lights_power);
        brightnessDownButton = (Button) this.activity.findViewById(R.id.darker);
        brightnessUpButton = (Button) this.activity.findViewById(R.id.brighter);
        brightnessMinButton = (Button) this.activity.findViewById(R.id.darkest);
        brightnessMaxButton = (Button) this.activity.findViewById(R.id.brightest);

    }

    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

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

        // Adds all listeners to GUI elements, to update internal parameters / take appropriate actions on change
        addGUIListeners();

    }

}
