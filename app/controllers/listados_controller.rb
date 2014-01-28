class ListadosController < ApplicationController
  before_action :set_listado, only: [:show, :edit, :update, :destroy]

  # GET /listados
  # GET /listados.json
  def index
    @listados = Listado.all
  end

  # GET /listados/1
  # GET /listados/1.json
  def show
  end

  # GET /listados/new
  def new
    @listado = Listado.new
  end

  # GET /listados/1/edit
  def edit
  end

  # POST /listados
  # POST /listados.json
  def create
    @listado = Listado.new(listado_params)

    respond_to do |format|
      if @listado.save
        format.html { redirect_to @listado, notice: 'Listado was successfully created.' }
        format.json { render action: 'show', status: :created, location: @listado }
      else
        format.html { render action: 'new' }
        format.json { render json: @listado.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /listados/1
  # PATCH/PUT /listados/1.json
  def update
    respond_to do |format|
      if @listado.update(listado_params)
        format.html { redirect_to @listado, notice: 'Listado was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @listado.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /listados/1
  # DELETE /listados/1.json
  def destroy
    @listado.destroy
    respond_to do |format|
      format.html { redirect_to listados_url }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_listado
      @listado = Listado.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def listado_params
      params.require(:listado).permit(:asignatura_id, :estudiantes)
    end
end
