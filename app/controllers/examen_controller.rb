class ExamenController < ApplicationController
  before_action :set_examan, only: [:show, :edit, :update, :destroy]

  def clave
    @examan = Examan.find(params[:id])
  end

  def show
  end

  def new
    @asignatura = Asignatura.find(params[:id])
    @examan = Examan.new
    @examan.asignatura_id = @asignatura.id
  end

  def edit
    @asignatura = @examan.asignatura
  end

  def get_etiquetas
    list = []
    for etiq in @examan.asignatura.listado_de_etiquetas
      list << etiq if params["etiqueta_#{etiq}"]
    end
    list.join(',')
  end

  def get_preguntas
    list = []
    for etiqueta in @examan.listado_de_etiquetas
      for pregunta in Preguntum.from_etiqueta(etiqueta)
        list << pregunta if params["pregunta_#{pregunta.id}"] && !list.include?(pregunta)
      end
    end
    list
  end

  def get_cantidades
    list = []
    for etiqueta in @examan.listado_de_etiquetas
      list << "#{etiqueta}:#{params["cantidad_#{etiqueta}"]}" if params["cantidad_#{etiqueta}"]
    end
    list.join('|')
  end

  def create
    @examan = Examan.new(examan_params)
    @examan.etiquetas = get_etiquetas

    respond_to do |format|
      if @examan.save
        format.html { redirect_to edit_examan_path(@examan), notice: 'Examan was successfully created.' }
        format.json { render action: 'show', status: :created, location: @examan }
      else
        format.html { render action: 'new' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  def update
    @examan.etiquetas = get_etiquetas
    @examan.pregunta = get_preguntas
    @examan.preguntas_por_tema = get_cantidades

    respond_to do |format|
      if @examan.update(examan_params)
        format.html { redirect_to edit_examan_path(@examan), notice: 'Examan was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /examen/1
  # DELETE /examen/1.json
  def destroy
    @examan.destroy
    respond_to do |format|
      format.html { redirect_to examen_url }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_examan
      @examan = Examan.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def examan_params
      params.require(:examan).permit(:nombre, :etiquetas, :directorio, :cantidad, :asignatura_id)
    end
end
