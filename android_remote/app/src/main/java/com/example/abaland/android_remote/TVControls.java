package com.example.abaland.android_remote;

import android.view.View;
import android.widget.Button;

import java.util.HashMap;


class TVControls {

    private MainActivity activity;

    private HashMap<String, String> ButtonToInstructionMapping = new HashMap<>();

    private Button powerButton;
    private Button volumeDownButton;
    private Button volumeUpButton;


    TVControls (MainActivity activity) {

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

        MainActivity activity = TVControls.this.activity;

        activity.rabbitManager.publishMessage(RemoteName, KeyToPress, activity);

    }

    /**
     * Binds all elements from GUI (spinner, buttons, ...) to the script internal parameters
     */
    private void bindGUIToScript() {

        powerButton = (Button) this.activity.findViewById(R.id.tv_power);
        volumeDownButton = (Button) this.activity.findViewById(R.id.volumedown);
        volumeUpButton = (Button) this.activity.findViewById(R.id.volumeup);

    }

    /**
     * Adds all listeners to GUI elements, to update internal parameters, send commands, ...
     */
    private void addGUIListeners() {

        powerButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        volumeDownButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

        volumeUpButton.setOnClickListener(new Button.OnClickListener() {

            @Override
            public void onClick(View v){onClickFunction(v);}

        });

    }

    void initialize() {

        // Initializes the mapping between text on the buttons and the instruction to send
        ButtonToInstructionMapping.put("Power", "KEY_POWER");
        ButtonToInstructionMapping.put("Vol+", "KEY_VOLUMEUP");
        ButtonToInstructionMapping.put("Vol-", "KEY_VOLUMEDOWN");

        // Links all GUI items to the script
        bindGUIToScript();

        // Adds listeners to GUI, to update internal parameters/take appropriate actions on change
        addGUIListeners();

    }

}
