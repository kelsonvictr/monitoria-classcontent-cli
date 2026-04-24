package com.example;

import java.util.HashMap;
import java.util.Map;

// Nome da classe errado (minúsculo)
public class userService {

    private Map<String, Object> dados = new HashMap<>();

    public void processarDados(int quantidade, String tipo) {
        // Variável de uma letra
        int x = quantidade * 2;

        try {
            // Operação que pode falhar
            dados.put(tipo, x);
            System.out.println("Dados processados: " + x);
        } catch (Exception e) {
            // Catch vazio — péssima prática
        }

        // TODO: implementar validação
        if (tipo == "admin") {
            System.out.println("Admin detectado");
        }
    }

    public Object buscarDado(String chave) {
        return dados.get(chave)
    }
}
