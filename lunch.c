  while (1){
	  HAL_TIM_Base_Start(&htim16);
	  uint8_t number =0;
	  uint8_t specialNumber = 83;
	  while(1){
		  HAL_UART_Receive(&huart2, &number, sizeof(uint8_t), 100);
		  if (number==specialNumber){
			  HAL_GPIO_WritePin(Green_GPIO_Port, Green_Pin, 1);

			  break;

		  }
	  }
	  HAL_Delay(500);

	  while(1){
		  HAL_UART_Receive(&huart1, &number, sizeof(uint8_t), 100);


		  if (number == specialNumber){


			  HAL_GPIO_WritePin(Green_GPIO_Port, Green_Pin, 1);

			  HAL_Delay(250);
			  HAL_UART_Transmit(&huart1, &number, sizeof(uint8_t), 100);
			  HAL_UART_Transmit(&huart2, &number, sizeof(uint8_t), 100);

			  number = 0;
		  }
		  else{
		  HAL_GPIO_WritePin(Green_GPIO_Port, Green_Pin, 0);


		  }

	  }
	      /* USER CODE END WHILE */

	      /* USER CODE BEGIN 3 */
	}
	    /* USER CODE END 3 */
}
