package com.example;

// Controller sem erros graves — para balancear o score
public class HomeController {

    private final userService userService;

    public HomeController(userService userService) {
        this.userService = userService;
    }

    public String home() {
        return "index";
    }

    public String processar(int id, String nome) {
        userService.processarDados(id, nome);
        return "redirect:/home";
    }
}
