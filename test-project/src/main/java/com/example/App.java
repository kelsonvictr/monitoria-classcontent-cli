package com.example;

import java.util.ArrayList;
import java.util.List;

// Classe principal do projeto
public class App {

    public static void main(String[] args) {
        System.out.println("Hello World!");

        // Variáveis com nomes ruins
        int a = 10;
        String b = "teste";
        double c = 3.14

        // Faltou fechar o parêntese
        List<String> nomes = new ArrayList<>(;

        // Classe que chama o serviço
        userService service = new userService();
        service.processarDados(a, b);
    }
}
